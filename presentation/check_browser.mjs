// Optional browser smoke check: Node 22+ and Chrome; synthetic demo only.
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {mkdtemp, readFile, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const here = fileURLToPath(new URL('.', import.meta.url));
const page = pathToFileURL(join(here, 'examples/handoffs.html')).href;
const chrome = process.argv[2] || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const directory = await mkdtemp(join(tmpdir(), 'ci-presentation-check-'));
const child = spawn(chrome, ['--headless=new', '--no-first-run', '--no-default-browser-check',
  '--disable-background-networking', '--remote-debugging-port=0', '--user-data-dir=' + directory], {stdio:['ignore','ignore','pipe']});
let launchError='';
child.stderr.on('data', data => { launchError += data.toString(); });
child.on('error', error => { launchError += error.message; });
const deadline = setTimeout(() => { child.kill(); process.exit(1); }, 45000);
let socket;
const pause = () => new Promise(resolve => setTimeout(resolve, 100));
async function waitFor(check) {
  for (let i=0; i<120; i++) { if (await check()) return; await pause(); }
  throw new Error('Browser check timed out. ' + launchError.slice(-1500));
}

try {
  let port;
  await waitFor(async () => {
    try { port = Number((await readFile(join(directory, 'DevToolsActivePort'), 'utf8')).split('\n')[0]); return port > 0; }
    catch { return false; }
  });
  const targets = await (await fetch('http://127.0.0.1:' + port + '/json/list')).json();
  socket = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener('open', resolve, {once:true});
    socket.addEventListener('error', reject, {once:true});
  });
  let sequence=0, dialogAnswer=false, dialogs=0;
  const pending=new Map(), exceptions=[], network=[];
  const command=(method, params={}) => new Promise((resolve,reject) => {
    const id=++sequence; pending.set(id,{resolve,reject});
    socket.send(JSON.stringify({id,method,params}));
  });
  socket.addEventListener('message', event => {
    const data=JSON.parse(event.data);
    if (pending.has(data.id)) {
      const task=pending.get(data.id); pending.delete(data.id);
      data.error ? task.reject(new Error(JSON.stringify(data.error))) : task.resolve(data.result);
    }
    if (data.method === 'Runtime.exceptionThrown') exceptions.push(data.params);
    if (data.method === 'Network.requestWillBeSent' && /^https?:/.test(data.params.request.url)) network.push(data.params.request.url);
    if (data.method === 'Page.javascriptDialogOpening') {
      dialogs++;
      command('Page.handleJavaScriptDialog', {accept:dialogAnswer}).catch(error => exceptions.push(String(error)));
    }
  });
  const evaluate=async expression => {
    const result=await command('Runtime.evaluate', {expression,returnByValue:true,awaitPromise:true,userGesture:true});
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await command('Page.enable'); await command('Runtime.enable'); await command('Network.enable');
  await command('Browser.setDownloadBehavior', {behavior:'allow',downloadPath:directory});
  const settle=() => evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
  const fits=() => evaluate('({reading:document.documentElement.classList.contains("reading"),width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,viewportWidth:innerWidth,viewportHeight:innerHeight})');
  await command('Emulation.setDeviceMetricsOverride', {width:1280,height:800,deviceScaleFactor:1,mobile:false});
  await command('Page.navigate', {url:page});
  await waitFor(() => evaluate('document.querySelector("nav") && !document.querySelector("nav").hidden'));
  await settle();
  const assertFits=async label => {
    const layout=await fits();
    assert.equal(layout.reading,false,label+': '+JSON.stringify(layout));
    assert.ok(layout.width<=layout.viewportWidth && layout.height<=layout.viewportHeight,label+': '+JSON.stringify(layout));
  };
  await assertFits('Prepare at 1280 × 800');
  const screenshot=async name => {
    // Capture the settled active state, after the template's utility transitions.
    await new Promise(resolve => setTimeout(resolve,400));
    const result=await command('Page.captureScreenshot', {format:'png'});
    await writeFile(join(directory,name),Buffer.from(result.data,'base64'));
  };
  await screenshot('desktop.png');
  await evaluate('document.querySelector("[data-view=practice]").focus()');
  await command('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});
  await command('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await settle();
  await assertFits('Practise at 1280 × 800');
  assert.equal(await evaluate('!document.querySelector("#practice").hidden && document.querySelector("#advice").hidden && document.querySelector(".notice").getBoundingClientRect().height > 0 && document.querySelector(".next").getBoundingClientRect().height > 0'),true);
  await evaluate('document.querySelector("#practice-note").value="A synthetic opening";document.querySelector("#practice-note").dispatchEvent(new Event("input"))');
  const editorRect=() => evaluate('JSON.stringify(document.querySelector("#practice-note").getBoundingClientRect().toJSON())');
  const before=await editorRect();
  for (const reference of ['example','sources','evidence']) {
    await evaluate('document.querySelector("[data-reference-button='+reference+']").click()');
    await settle();
    await assertFits('Reference '+reference);
    assert.equal(await editorRect(),before,'Opening a reference must not move the editor');
    assert.equal(await evaluate('document.querySelector("#practice-note").value'),'A synthetic opening');
  }
  await evaluate('document.querySelector("[data-reference-button=example]").click()');
  await settle();
  await screenshot('practice.png');
  await evaluate('document.querySelector("#reference-close").click()');
  await settle();
  assert.equal(await editorRect(),before,'Closing a reference must not move the editor');
  assert.equal(await evaluate('document.activeElement.dataset.referenceButton'),'example');
  await evaluate('document.querySelector("[data-reference-button=example]").click();document.querySelector("#export-notes").click()');
  let exported;
  await waitFor(async () => { try {exported=JSON.parse(await readFile(join(directory,'compound-intelligence-notes.json'),'utf8'));return true;} catch{return false;} });
  assert.equal(exported.notes.practice,'A synthetic opening');
  assert.equal(exported.kind,'ci.presentation.notes.v1');
  const document=await command('DOM.getDocument');
  const input=await command('DOM.querySelector', {nodeId:document.root.nodeId,selector:'#import-notes'});
  const load=path => command('DOM.setFileInputFiles', {nodeId:input.nodeId,files:[path]});
  // Accept replacement only for this explicit round-trip check.
  dialogAnswer=true;
  await evaluate('document.querySelector("#practice-note").value="Changed locally";document.querySelector("#practice-note").dispatchEvent(new Event("input"))');
  await load(join(directory,'compound-intelligence-notes.json'));
  await waitFor(() => evaluate('document.querySelector("#notes-status").textContent.startsWith("Notes loaded")'));
  assert.equal(await evaluate('document.querySelector("#practice-note").value'),'A synthetic opening');
  const wrong=join(directory,'wrong-case.json');
  await writeFile(wrong,JSON.stringify({...exported,packet_sha256:'wrong-case'}));
  await load(wrong);
  await waitFor(() => evaluate('document.querySelector("#notes-status").textContent.startsWith("Could not load")'));
  assert.equal(await evaluate('document.querySelector("#practice-note").value'),'A synthetic opening');
  // A cancelled replacement must keep unsaved notes.
  dialogAnswer=false; const previousDialogs=dialogs;
  await evaluate('document.querySelector("#practice-note").value="Keep this edit";document.querySelector("#practice-note").dispatchEvent(new Event("input"))');
  await load(join(directory,'compound-intelligence-notes.json'));
  await waitFor(async () => dialogs > previousDialogs && await evaluate('document.querySelector("#import-notes").value === ""'));
  assert.equal(await evaluate('document.querySelector("#practice-note").value'),'Keep this edit');
  await evaluate('document.querySelector("[data-view=reflection]").click()');
  await settle();
  assert.equal(await evaluate('!document.querySelector("#reflection").hidden'),true);
  await assertFits('Reflect at 1280 × 800');
  assert.equal(await evaluate('!document.querySelector("[data-reference=example]").hidden'),true,'Reference remains open across tasks');
  await screenshot('reflection.png');
  await command('Emulation.setDeviceMetricsOverride', {width:1366,height:768,deviceScaleFactor:1,mobile:false});
  for (const view of ['advice','practice','reflection']) {
    await evaluate('document.querySelector("[data-view='+view+']").click()');
    await settle();
    await assertFits(view+' at 1366 × 768');
  }
  // A reading activity reveals all supplied tasks without losing the draft.
  await evaluate('document.querySelector("#layout-toggle").click()');
  assert.equal(await evaluate('document.documentElement.classList.contains("reading") && getComputedStyle(document.querySelector("#practice")).display !== "none"'),true);
  assert.equal(await evaluate('document.querySelector("#practice-note").value'),'Keep this edit');
  await evaluate('document.querySelector("#layout-toggle").click()');
  await settle();
  await assertFits('Return from reading');
  // Unusually long supplied text must reflow, never silently clip or truncate.
  await evaluate('window.originalAdvice=document.querySelector(".next .text").textContent;document.querySelector(".next .text").textContent="A longer supplied response. ".repeat(120)');
  await waitFor(() => evaluate('document.documentElement.classList.contains("reading")'));
  assert.equal(await evaluate('document.querySelector(".next .text").textContent.length'),'A longer supplied response. '.repeat(120).length);
  await evaluate('document.querySelector(".next .text").textContent=window.originalAdvice;document.querySelector("#layout-toggle").click()');
  await settle();
  await assertFits('Return after long text');
  await evaluate('document.querySelector("[data-view=advice]").click()');
  await command('Emulation.setDeviceMetricsOverride', {width:390,height:1000,deviceScaleFactor:1,mobile:true});
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth'),true);
  await screenshot('mobile.png');
  await command('Emulation.setDeviceMetricsOverride', {width:320,height:800,deviceScaleFactor:1,mobile:false});
  assert.equal(await evaluate('document.documentElement.scrollWidth <= innerWidth && getComputedStyle(document.querySelector(".kind")).display !== "none"'),true);
  await command('Emulation.setEmulatedMedia',{media:'print'});
  assert.equal(await evaluate('Array.from(document.querySelectorAll(".view,[data-reference]")).every(element => getComputedStyle(element).display !== "none")'),true);
  await command('Emulation.setEmulatedMedia',{media:''});
  // Reload only this isolated synthetic page to exercise the script-free fallback.
  dialogAnswer=true;
  await command('Emulation.setScriptExecutionDisabled',{value:true});
  await command('Page.navigate',{url:page});
  await waitFor(() => evaluate('document.readyState === "complete" && !document.documentElement.classList.contains("interactive")'));
  assert.equal(await evaluate('Array.from(document.querySelectorAll(".view")).every(element => getComputedStyle(element).display !== "none") && !!document.querySelector("#practice details")'),true);
  assert.deepEqual(exceptions,[]); assert.deepEqual(network,[]);
  console.log(JSON.stringify({status:'passed',checks:['no desktop scrolling at 1280×800 and 1366×768','keyboard task switching','persistent advice and uncertainty','references do not move the editor','notes export/import','wrong-case rejection','cancelled replacement','reading mode and long-content reflow','390px and 320px reflow','print and script-free fallback','no page network requests or script exceptions'],previews:directory},null,2));
} finally {clearTimeout(deadline);socket?.close();child.kill();}
