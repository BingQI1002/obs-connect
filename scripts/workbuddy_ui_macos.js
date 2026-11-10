/* JXA / macOS System Events. Only edits WorkBuddy's Instructions field. */
ObjC.import('Foundation');
ObjC.import('AppKit');
// CF accessibility objects are toll-free bridged. Explicit id signatures avoid
// JXA treating AXUIElementRef/CFTypeRef as opaque Ref values.
ObjC.bindFunction('AXUIElementCreateApplication', ['id',['int']]);
ObjC.bindFunction('AXUIElementCopyAttributeValue', ['int',['id','id','id*']]);
ObjC.bindFunction('AXUIElementSetAttributeValue', ['int',['id','id','id']]);
ObjC.bindFunction('AXUIElementPerformAction', ['int',['id','id']]);
ObjC.bindFunction('AXIsProcessTrusted', ['bool',[]]);

function readPinnedPlan(path, expected) {
  if (!expected) throw Error('plan_hash_required');
  const data=$.NSFileManager.defaultManager.contentsAtPath($(path));
  if (!data) throw Error('plan_missing');
  const task=$.NSTask.alloc.init, output=$.NSPipe.pipe, input=$.NSPipe.pipe;
  task.launchPath='/usr/bin/shasum'; task.arguments=$(['-a','256']);
  task.standardInput=input; task.standardOutput=output;
  task.launch;
  input.fileHandleForWriting.writeData(data); input.fileHandleForWriting.closeFile;
  task.waitUntilExit;
  const hashText=ObjC.unwrap($.NSString.alloc.initWithDataEncoding(output.fileHandleForReading.readDataToEndOfFile,$.NSUTF8StringEncoding));
  if(Number(task.terminationStatus)!==0 || hashText.trim().split(/\s+/)[0]!==expected)
    throw Error('plan_changed: 计划与审批时的摘要不同');
  // Hash and parse the same captured bytes, not two separate file reads.
  const plan=JSON.parse(ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data,$.NSUTF8StringEncoding)).replace(/^\uFEFF/,''));
  if(plan.schema!==1 || plan.host!=='workbuddy' || plan.kind!=='ui-field' ||
      plan.target!=='WorkBuddy/设置/个性化/给 WorkBuddy 的指令' ||
      typeof plan.before!=='string' || typeof plan.after!=='string') throw Error('invalid_ui_plan');
  return plan;
}

function withTemporaryClipboard(pb, markup, text, callback) {
  const saved=[], items=pb.pasteboardItems;
  for(let i=0;items && i<Number(items.count);i++) {
    const original=items.objectAtIndex(i), copy=$.NSPasteboardItem.alloc.init;
    for(let j=0;j<Number(original.types.count);j++) {
      const type=original.types.objectAtIndex(j), data=original.dataForType(type);
      if (!data || !copy.setDataForType(data,type)) throw Error('clipboard_snapshot_incomplete');
    }
    saved.push(copy);
  }
  let ownedCount=null;
  try {
    pb.clearContents; ownedCount=Number(pb.changeCount);
    const htmlOK=pb.setStringForType($(markup),$('public.html')); ownedCount=Number(pb.changeCount);
    if (!htmlOK) throw Error('clipboard_write_failed');
    const textOK=pb.setStringForType($(text),$('public.utf8-plain-text')); ownedCount=Number(pb.changeCount);
    if (!textOK) throw Error('clipboard_write_failed');
    return callback(()=>{if(Number(pb.changeCount)!==ownedCount) throw Error('clipboard_user_intervened');});
  } finally {
    if(ownedCount!==null && Number(pb.changeCount)===ownedCount) {
      pb.clearContents;
      if(saved.length && !pb.writeObjects($(saved))) throw Error('clipboard_restore_failed');
    }
  }
}

function clipboardCheck() {
  const pb=$.NSPasteboard.pasteboardWithUniqueName;
  const original='原剪贴板测试 🍅', html='<b>原剪贴板测试</b>';
  pb.clearContents;
  pb.setStringForType($(original),$('public.utf8-plain-text'));
  pb.setStringForType($(html),$('public.html'));
  const check=()=>{
    if(ObjC.unwrap(pb.stringForType($('public.utf8-plain-text')))!==original ||
       ObjC.unwrap(pb.stringForType($('public.html')))!==html) throw Error('clipboard_roundtrip_failed');
  };
  withTemporaryClipboard(pb,'<p>新值</p>','新值',guard=>guard()); check();
  try {withTemporaryClipboard(pb,'<p>失败路径</p>','失败路径',()=>{throw Error('intentional_failure');});}
  catch(error) {if(String(error).indexOf('intentional_failure')<0) throw error;}
  check(); pb.clearContents;
  return {status:'passed',success_restore:true,failure_restore:true,scope:'unique named pasteboard only; general clipboard untouched'};
}

function run(argv) {
  const mode = argv[0], input = argv[1];
  if(mode==='clipboard-check') return JSON.stringify(clipboardCheck());
  if(mode==='plan-check') {
    const plan=readPinnedPlan(input,argv[2]);
    return JSON.stringify({status:'passed',host:plan.host,target:plan.target,hash_verified:true});
  }
  if (!['inspect', 'apply'].includes(mode) || !input) throw Error('Usage: inspect OUTPUT.txt | apply PLAN.json SHA256');
  let pinnedPlan=null;
  if(mode==='apply') {
    try {pinnedPlan=readPinnedPlan(input,argv[2]);}
    catch(error) {return JSON.stringify({status:'plan_invalid',message:String(error),saved_verified:false});}
  }
  if(!$.AXIsProcessTrusted()) return JSON.stringify({status:'needs_system_permission',saved_verified:false,
    message:'当前执行宿主没有可用的辅助功能访问；Agent 先申请本次原生命令执行授权，再核 macOS 辅助功能/自动化授权'});
  const se = Application('System Events');
  let process;
  try {
    process=se.processes.byName('WorkBuddy');
    if(!process.exists()) return JSON.stringify({status:'needs_app_open',message:'请由 Agent 打开 WorkBuddy 后重试'});
  } catch(error) {return JSON.stringify({status:'needs_system_permission',message:String(error),saved_verified:false});}
  const titleAliases = ['给 WorkBuddy 的指令', 'Instructions for WorkBuddy', '自定义指令', 'Custom instructions'];
  const get = (fn, fallback) => { try { return fn(); } catch (_) { return fallback; } };
  const appRef = $.AXUIElementCreateApplication(process.unixId());
  function axValue(ref, key) {
    const output = Ref();
    return Number($.AXUIElementCopyAttributeValue(ref, $(key), output)) === 0 ? output[0] : null;
  }
  function AXNode(ref) {
    this.ref = ref;
    this.attributes = {byName: key => ({value: () => {
      const result = axValue(ref,key); return result ? ObjC.unwrap(result) : null;
    }})};
    this.uiElements = () => axNodes(axValue(ref,'AXChildren'));
    this.name = () => ObjC.unwrap(axValue(ref,'AXTitle')) || '';
    this.description = () => ObjC.unwrap(axValue(ref,'AXDescription')) || '';
    this.value = () => ObjC.unwrap(axValue(ref,'AXValue')) || '';
    this.role = () => ObjC.unwrap(axValue(ref,'AXRole')) || '';
    this.focus = () => Number($.AXUIElementSetAttributeValue(ref,$('AXFocused'),$(true)));
    this.click = () => {
      const code = Number($.AXUIElementPerformAction(ref,$('AXPress')));
      if (code !== 0) {
        if (this.focus() !== 0) throw Error('AXPress/focus failed: '+code);
      }
    };
  }
  function axNodes(array) {
    if (!array) return [];
    const result = [];
    for(let i=0;i<Number(array.count);i++) result.push(new AXNode(array.objectAtIndex(i)));
    return result;
  }
  const labels = el => [get(() => el.name(), ''), get(() => el.description(), ''),
    get(() => el.attributes.byName('AXTitle').value(), ''),
    get(() => el.attributes.byName('AXDescription').value(), ''),
    get(() => el.value(), '')].filter(v => typeof v === 'string' && v.length);
  const name = el => labels(el).sort((a,b) => b.length-a.length)[0] || '';
  const matches = (el, choices) => labels(el).some(label => choices.includes(label));
  const role = el => String(get(() => el.role(), '') || '');
  const value = el => String(get(() => el.value(), '') || '');
  const normal = s => String(s).replace(/\s+/g, ' ').trim();
  function flatten(root) {
    let out = [], count = 0;
    function visit(el, depth) {
      if (++count > 5000 || depth > 35) return;
      out.push(el);
      for (const child of get(() => el.uiElements(), [])) visit(child, depth + 1);
    }
    visit(root, 0); return out;
  }
  function waitFor(fn, seconds) {
    const end = Date.now() + seconds * 1000;
    do {
      try { const result=fn(); if (result) return result; } catch (_) {}
      delay(0.25);
    } while (Date.now() < end);
    throw Error('ui_not_ready: WorkBuddy 设置界面未就绪或层级不受支持；未继续保存');
  }
  function windows() { return axNodes(axValue(appRef,'AXWindows')); }
  function press(el) {
    if (role(el)==='AXButton') {
      if (!process.frontmost()) throw Error('user_intervened: WorkBuddy 已不在前台');
      // AppleScript handles the native point type more reliably than JXA's
      // generic Apple-event converter. Only fixed UI labels enter this source.
      const allowed=['个性化','Personalization','编辑','Edit','取消','Cancel','保存','Save','当前内容为空，点击开始输入','Click to start typing'];
      const wanted=labels(el).find(label => allowed.includes(label));
      if (!wanted) throw Error('unsupported_button_label');
      const quoted='"'+wanted.replace(/\\/g,'\\\\').replace(/"/g,'\\"')+'"';
      const source='tell application "System Events"\n tell process "WorkBuddy"\n'+
        ' repeat with windowIndex from 1 to (count of windows)\n'+
        ' set controlList to entire contents of window windowIndex\n'+
        ' repeat with controlIndex from 1 to (count of controlList)\n'+
        '  set itemRef to item controlIndex of controlList\n'+
        '  try\n   if (role of itemRef as text) is "AXButton" then\n'+
        '    set matchedLabel to false\n'+
        '    repeat with attributeName in {"AXTitle", "AXDescription", "AXValue"}\n'+
        '     try\n      if ((value of attribute (contents of attributeName) of itemRef) as text) is '+quoted+' then set matchedLabel to true\n     end try\n'+
        '    end repeat\n    try\n     if (name of itemRef as text) is '+quoted+' then set matchedLabel to true\n    end try\n'+
        '    if matchedLabel then\n'+
        '     try\n      set {px, py} to position of itemRef\n      set {sw, sh} to size of itemRef\n'+
        '      click at {((px + sw / 2) as integer), ((py + sh / 2) as integer)}\n      return "clicked"\n'+
        '     on error errorText\n      return "click_error: " & errorText\n     end try\n'+
        '    end if\n   end if\n  end try\n end repeat\n end repeat\n end tell\nend tell\nreturn "not_found"';
      const error=Ref(), result=$.NSAppleScript.alloc.initWithSource($(source)).executeAndReturnError(error);
      if (result && ObjC.unwrap(result.stringValue)==='clicked') return;
      throw Error('native_button_click_failed: '+wanted+' / '+(result ? ObjC.unwrap(result.stringValue) : 'script_error'));
    }
    el.click();
  }
  function menuItems(menuLabel) {
    const bar = new AXNode(axValue(appRef,'AXMenuBar'));
    const item = bar.uiElements().find(el => matches(el,menuLabel));
    if (!item) throw Error('native_menu_missing: '+menuLabel.join('/'));
    press(item);
    const menu = waitFor(() => item.uiElements().find(el => role(el)==='AXMenu'),3);
    return menu.uiElements();
  }
  function editMenu(labels) {
    const allowed=['全选','Select All','粘贴','Paste'];
    if (!labels.every(label => allowed.includes(label))) throw Error('unsupported_edit_command');
    const itemNames='{'+labels.map(label=>'"'+label+'"').join(',')+'}';
    const source='tell application "System Events"\n tell process "WorkBuddy"\n'+
      ' repeat with menuLabel in {"编辑", "Edit"}\n  try\n'+
      '   click menu bar item (contents of menuLabel) of menu bar 1\n'+
      '   repeat with itemLabel in '+itemNames+'\n    try\n'+
      '     click menu item (contents of itemLabel) of menu 1 of menu bar item (contents of menuLabel) of menu bar 1\n'+
      '     return "selected"\n    end try\n   end repeat\n  end try\n end repeat\n end tell\nend tell\nreturn "not_found"';
    const error=Ref(), result=$.NSAppleScript.alloc.initWithSource($(source)).executeAndReturnError(error);
    if (!result || ObjC.unwrap(result.stringValue)!=='selected') throw Error('edit_menu_item_missing: '+labels.join('/'));
  }
  function fieldWindow() {
    for (const win of windows()) {
      const nodes=flatten(win);
      if(nodes.some(el => role(el)==='AXHeading' && matches(el,titleAliases)) &&
          nodes.some(el => role(el)==='AXButton' && matches(el,['个性化','Personalization']))) return win;
    }
    return null;
  }
  function clickNamed(root, labels) {
    const el = flatten(root).find(el => role(el) === 'AXButton' && matches(el, labels));
    if (!el) throw Error('ui_control_missing: ' + labels.join('/'));
    press(el); return el;
  }
  function readPreview(win) {
    const all = flatten(win);
    let index = all.findIndex(el => matches(el, titleAliases));
    if (index < 0) return null;
    let editPassed = false;
    for (const el of all.slice(index + 1)) {
      if (role(el) !== 'AXButton') continue;
      if (!editPassed && matches(el, ['编辑','Edit'])) { editPassed = true; continue; }
      if (editPassed) {
        const chunks=flatten(el).filter(child => role(child)==='AXStaticText').map(child => value(child)||name(child));
        const text = chunks.length===1 ? chunks[0] : name(el);
        return ['例如：回答尽量简洁，先给结论','e.g. Keep answers concise and lead with the conclusion'].includes(text.trim()) ? '' : text;
      }
    }
    return null;
  }
  function readEditor(win, allowEmpty) {
    const editor = flatten(win).find(el => role(el) === 'AXTextArea');
    if (!editor) return null;
    let parent = axValue(editor.ref,'AXParent'), correctDialog = false;
    for (let depth=0;parent && depth<12;depth++) {
      const node = new AXNode(parent), descendants = flatten(node);
      if (descendants.some(el => role(el)==='AXButton' && matches(el,['保存','Save']))) {
        correctDialog = descendants.some(el => role(el)==='AXHeading' && matches(el,titleAliases));
        break;
      }
      parent = axValue(parent,'AXParent');
    }
    if (!correctDialog) throw Error('wrong_editor_dialog: 当前编辑器不是 WorkBuddy 指令字段');
    const rawValue = axValue(editor.ref,'AXValue');
    const emptyPlaceholder = flatten(win).some(el => role(el)==='AXButton' && /当前内容为空，点击开始输入|Click to start typing/.test(name(el)));
    if (!rawValue && !emptyPlaceholder && !allowEmpty) throw Error('editor_value_unreadable: 不能把不可读字段当作空指令');
    let text = rawValue ? String(ObjC.unwrap(rawValue)) : '';
    if (!text && !emptyPlaceholder && editor.uiElements().some(el => value(el).trim()))
      throw Error('editor_value_incomplete: 不能覆盖未完整读取的指令');
    if (/^(当前内容为空，点击开始输入|Click to start typing|Current content is empty)/.test(text.trim())) text = '';
    return {editor, text};
  }
  function savePrivate(path, text) {
    if ($.NSFileManager.defaultManager.fileExistsAtPath($(path))) throw Error('output_exists: 不覆盖已有读取副本');
    const ok = $(text).writeToFileAtomicallyEncodingError($(path), true, $.NSUTF8StringEncoding, null);
    if (!ok) throw Error('output_not_writable');
    $.NSFileManager.defaultManager.setAttributesOfItemAtPathError($({NSFilePosixPermissions:384}), $(path), null);
  }
  let win, editorState, stage = 'settings-menu', ownEditor=false, baselineText=null,
      proposedText=null, didSave=false;
  try {
    process.frontmost = true;
    // Use the app's native Settings menu; do not guess screen coordinates.
    win = fieldWindow();
    if (!win) {
      const settings = menuItems(['WorkBuddy']).find(el => /^(设置|Settings|Preferences)(…|\.\.\.)?$/.test(name(el)));
      if (!settings) throw Error('settings_menu_missing');
      press(settings);
      stage = 'personalization-navigation';
      win = waitFor(() => windows().find(w => flatten(w).some(el => matches(el, ['个性化','Personalization']))), 12);
      $.AXUIElementPerformAction(win.ref,$('AXRaise'));
      clickNamed(win, ['个性化','Personalization']);
    }
    stage = 'instructions-section';
    win = waitFor(fieldWindow, 8);
    if (flatten(win).some(el => role(el)==='AXTextArea'))
      throw Error('settings_editor_busy: 请先结束现有编辑，Agent 再自动继续，不覆盖未保存草稿');
    let savedBefore = readPreview(win);
    if (savedBefore===null) throw Error('instructions_preview_unreadable');
    if (mode === 'inspect' && savedBefore !== '') {
      savePrivate(input,savedBefore);
      return JSON.stringify({status:'inspected',field:'给 WorkBuddy 的指令',output:input,characters:savedBefore.length});
    }
    const all = flatten(win), heading = all.findIndex(el => matches(el, titleAliases));
    const edit = all.slice(heading + 1).find(el => role(el) === 'AXButton' && matches(el, ['编辑','Edit']));
    if (!edit) throw Error('instructions_edit_missing');
    press(edit);
    stage = 'instructions-editor';
    editorState = waitFor(() => readEditor(win), 8);
    ownEditor=true; baselineText=editorState.text;
    if(savedBefore==='' && editorState.text.trim()) savedBefore=editorState.text;
    if (mode === 'inspect') {
      savePrivate(input, editorState.text);
      clickNamed(win, ['取消','Cancel']);
      return JSON.stringify({status:'inspected', field:'给 WorkBuddy 的指令', output:input, characters:editorState.text.length});
    }
    const plan = pinnedPlan;
    proposedText=plan.after;
    if (normal(savedBefore) !== normal(plan.before)) throw Error('field_changed: 指令已变化，重读并重新准备计划');
    if (normal(savedBefore) === normal(plan.after)) {
      clickNamed(win, ['取消','Cancel']);
      return JSON.stringify({status:'already_applied', field:'给 WorkBuddy 的指令', readback:true});
    }
    // Activate an empty editor before pasting; preserve all existing instructions in plan.after.
    const placeholder = flatten(win).find(el => role(el) === 'AXButton' && /当前内容为空，点击开始输入|Click to start typing/.test(name(el)));
    if (placeholder) {
      press(placeholder);
      waitFor(()=>!flatten(win).some(el => role(el)==='AXButton' && /当前内容为空，点击开始输入|Click to start typing/.test(name(el))),5);
      editorState=readEditor(win,true);
    } else {
      editorState.editor.focus();
      editorState.editor.click();
    }
    const pb = $.NSPasteboard.generalPasteboard;
    const escape = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    const markup = plan.after.split('\n').map(line => '<p>'+(line ? escape(line) : '<br>')+'</p>').join('');
    stage='clipboard-paste';
    withTemporaryClipboard(pb,markup,plan.after,clipboardOwned=>{
      if (editorState.text.trim()) {
        const compact=text=>String(text).replace(/[\s\uFFFC]+/g,'');
        let selectedAll=false;
        for(let attempt=0;attempt<3 && !selectedAll;attempt++) {
          editMenu(['全选','Select All']);
          try {
            waitFor(()=>{
              const state=readEditor(win), selected=axValue(state.editor.ref,'AXSelectedText');
              return selected && compact(ObjC.unwrap(selected))===compact(state.text);
            },2);
            selectedAll=true;
          } catch (_) {}
        }
        if (!selectedAll) throw Error('selection_incomplete: 未全选完整指令，不执行替换');
        se.keyCode(51);
        waitFor(()=>{
          const state=readEditor(win,true), text=state.text.trim();
          return !text || /^(标题|Heading)\s*[1-6]$/.test(text);
        },5);
      }
      clipboardOwned(); editMenu(['粘贴','Paste']);
      waitFor(() => { const state = readEditor(win); return state && normal(state.text) === normal(plan.after); }, 8);
    });
    stage='save-and-readback';
    clickNamed(win, ['保存','Save']); didSave=true;
    waitFor(() => { const text = readPreview(win); return text !== null && normal(text) === normal(plan.after); }, 8);
    return JSON.stringify({status:'applied', field:'给 WorkBuddy 的指令', readback:true, new_conversation:'未验'});
  } catch (error) {
    // Never save unverified text or move anything to long-term memory as a fallback.
    let cancelledOwnDraft=false;
    if (ownEditor && !didSave) {
      try {
        const state=readEditor(win);
        if (state && (normal(state.text)===normal(baselineText) ||
            (proposedText!==null && normal(state.text)===normal(proposedText)))) {
          clickNamed(win,['取消','Cancel']); cancelledOwnDraft=true;
        }
      } catch (_) {}
    }
    const message=String(error);
    let status='ui_not_verified';
    if(/not authorized|not permitted|assistive access|辅助访问|未被授权|-1743|-1719|-25211/i.test(message)) status='needs_system_permission';
    else if(/user_intervened|clipboard_user_intervened/.test(message)) status='user_intervened';
    else if(/field_changed|plan_changed|invalid_ui_plan/.test(message)) status='plan_stale_or_invalid';
    else if(/settings_editor_busy/.test(message)) status='waiting_for_existing_edit';
    else if(/output_exists/.test(message)) status='inspection_output_exists';
    return JSON.stringify({status:status, stage:stage, message:message, saved_verified:false,
      cancelled_own_draft:cancelledOwnDraft,
      next:'Agent 先核系统辅助功能/自动化授权或重新读取界面；不要要求用户复制粘贴，也不要退写 MEMORY.md'});
  }
}
