---
name: davinci-resolve
description: 'Scripting, automation, and plugin development for DaVinci Resolve. Covers the Resolve scripting API (Python/Lua), Workflow Integration panels (Electron/JS), and Fusion Fuse plugins (Lua). Use when building tools that control Resolve, embed UI panels in Resolve, or add custom Fusion nodes/effects.'
---

# DaVinci Resolve Development

This skill covers the three official extension paths for DaVinci Resolve: app-level scripting, embedded Workflow Integration panels, and Fusion Fuse plugins.

---

## Extension Paths at a Glance

| Path | Language | Entry point | Use for |
|---|---|---|---|
| **Scripting API** | Python 3.6–3.12 / Lua | `import DaVinciResolveScript as dvr` | Project/timeline/media/render automation |
| **Workflow Integrations** | Electron (JS) + Python/Lua | Custom Electron app loaded in Resolve panel | Embedded UI panels (Studio only) |
| **Fusion Fuse** | Lua | `.fuse` file, `FuRegisterClass` entry | Custom Fusion tools/effects/generators |

- Workflow Integrations require **DaVinci Resolve Studio** (paid).
- External Python scripting (outside the built-in console) requires **Studio**. Free version is limited to the built-in Lua/Python console.
- Since Resolve 19.1, UIManager-based script GUIs are also Studio-only.
- Use **Python 3.10–3.12** from python.org. Python 3.13+ has ABI changes that can crash `fusionscript`. On Windows, Python 3.11+ can cause segfaults with `fusionscript.dll` — prefer 3.10.

---

## Scripting API

### Environment Setup

Resolve must be running and a project must be open before any script connects. `scriptapp("Resolve")` returns `None` if Resolve is not running — always check.

**macOS**
```bash
export RESOLVE_SCRIPT_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/"
export RESOLVE_SCRIPT_LIB="/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
```

**Windows**
```bat
set RESOLVE_SCRIPT_API=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\
set RESOLVE_SCRIPT_LIB=C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll
set PYTHONPATH=%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules\
```
> Note: Windows paths must NOT include quotation marks, despite official documentation examples showing them.

**Linux**
```bash
export RESOLVE_SCRIPT_API="/opt/resolve/Developer/Scripting/"
export RESOLVE_SCRIPT_LIB="/opt/resolve/libs/Fusion/fusionscript.so"
export PYTHONPATH="$PYTHONPATH:$RESOLVE_SCRIPT_API/Modules/"
# For home-directory installs, replace /opt/resolve with /home/resolve
```

**Connect in Python**
```python
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
assert resolve, "Resolve is not running or no project is open"
```

### Running Scripts

- **Built-in console** (Workspace > Scripts Console): paste and run directly; supports Python 2.7, 3.6, and Lua.
- **External terminal** (Studio only): `python3 my_script.py` with env vars set.
- **Scripts menu**: place `.py`/`.lua` files in the Utility Scripts folder and launch from Workspace > Scripts.
  - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Comp/`
  - Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Comp\`
  - Linux: `/opt/resolve/Fusion/Scripts/Comp/`
- **Headless mode**: launch Resolve with `-nogui` to run without UI. Scripting APIs still work.

Shipped examples:
- macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Examples/`
- Windows: `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Examples\`

### Object Hierarchy

The API is a hierarchical object model. Every operation chains downward from `Resolve`.

```
Resolve
├── Fusion()             → Fusion object (Fusion scripting entry point)
├── GetMediaStorage()    → MediaStorage
└── GetProjectManager()  → ProjectManager
    └── GetCurrentProject() → Project
        ├── GetMediaPool()   → MediaPool
        │   ├── GetRootFolder() → Folder
        │   │   └── GetClipList() → [MediaPoolItem]
        │   └── GetCurrentFolder() → Folder
        ├── GetCurrentTimeline() → Timeline
        │   └── GetItemListInTrack(type, idx) → [TimelineItem]
        └── Gallery
```

Resolve 20.3 documents **14 object classes** total: Resolve, ProjectManager, Project, MediaStorage, MediaPool, Folder, MediaPoolItem, Timeline, TimelineItem, Gallery, GalleryStill, GalleryStillAlbum, Graph (color page node graph, read-only), ColorGroup.

### API Reference — Key Methods Per Class

#### Resolve
| Method | Returns | Notes |
|---|---|---|
| `Fusion()` | `Fusion` | Entry point for Fusion scripts |
| `GetMediaStorage()` | `MediaStorage` | Query/act on media locations |
| `GetProjectManager()` | `ProjectManager` | Currently open database |
| `OpenPage(pageName)` | `None` | `"media"`, `"cut"`, `"edit"`, `"fusion"`, `"color"`, `"fairlight"`, `"deliver"` |

#### ProjectManager
| Method | Returns | Notes |
|---|---|---|
| `CreateProject(name)` | `Project` | Returns `None` if name not unique |
| `LoadProject(name)` | `Project` | Returns `None` if not found |
| `GetCurrentProject()` | `Project` | |
| `SaveProject()` | `Bool` | |
| `CloseProject(project)` | `Bool` | Does not save |
| `DeleteProject(name)` | `Bool` | Only if not currently loaded |
| `ImportProject(filePath)` | `Bool` | |
| `ExportProject(name, filePath)` | `Bool` | |
| `RestoreProject(filePath)` | `Bool` | From backup |
| `CreateFolder(name)` | `Bool` | |
| `OpenFolder(name)` | `Bool` | |
| `GotoRootFolder()` | `Bool` | |
| `GotoParentFolder()` | `Bool` | |
| `GetProjectListInCurrentFolder()` | `[names]` | |
| `GetFolderListInCurrentFolder()` | `[names]` | |

#### Project
| Method | Returns | Notes |
|---|---|---|
| `GetMediaPool()` | `MediaPool` | |
| `GetTimelineCount()` | `int` | |
| `GetTimelineByIndex(idx)` | `Timeline` | 1-based |
| `GetCurrentTimeline()` | `Timeline` | |
| `SetCurrentTimeline(tl)` | `Bool` | |
| `GetName()` / `SetName(name)` | `string` / `Bool` | |
| `GetSetting(key)` / `SetSetting(key, val)` | `string` / `Bool` | See Project Settings keys below |
| `GetRenderFormats()` | `{format→ext}` | |
| `GetRenderCodecs(format)` | `{desc→name}` | |
| `SetRenderSettings({...})` | `Bool` | Keys: `SelectAllFrames`, `MarkIn`, `MarkOut`, `TargetDir`, `CustomName` |
| `AddRenderJob()` | `Bool` | First call may fail silently in new project — add retry |
| `DeleteRenderJobByIndex(idx)` | `Bool` | |
| `DeleteAllRenderJobs()` | `Bool` | |
| `StartRendering(...)` | `Bool` | Overloaded: no args = all jobs; list of idx; `isInteractiveMode` kwarg |
| `StopRendering()` | `None` | |
| `IsRenderingInProgress()` | `Bool` | |
| `GetRenderJobStatus(idx)` | `{status, completion%}` | |
| `LoadRenderPreset(name)` | `Bool` | Presets must be created manually in Deliver page first |
| `SaveAsNewRenderPreset(name)` | `Bool` | |
| `GetPresetList()` | `[presets]` | |

**Project setting keys (selected):** `superScale` (0–3), `timelineFrameRate` (e.g. `"29.97 DF"` for drop-frame), `colorScienceMode`, `separateColorSpaceAndGamma`.

#### MediaStorage
| Method | Returns | Notes |
|---|---|---|
| `GetMountedVolumeList()` | `[paths]` | |
| `GetSubFolderList(path)` | `[paths]` | |
| `GetFileList(path)` | `[paths]` | |
| `RevealInStorage(path)` | `None` | |
| `AddItemListToMediaPool(items)` | `[MediaPoolItem]` | |

#### MediaPool
| Method | Returns | Notes |
|---|---|---|
| `GetRootFolder()` | `Folder` | |
| `GetCurrentFolder()` | `Folder` | |
| `SetCurrentFolder(folder)` | `Bool` | |
| `AddSubFolder(folder, name)` | `Folder` | |
| `ImportMedia([paths])` | `[MediaPoolItem]` | |
| `DeleteClips([clips])` | `Bool` | |
| `DeleteFolders([folders])` | `Bool` | |
| `MoveClips([clips], targetFolder)` | `Bool` | |
| `MoveFolders([folders], targetFolder)` | `Bool` | |
| `CreateEmptyTimeline(name)` | `Timeline` | |
| `AppendToTimeline([clips])` | `Bool` | |
| `AppendToTimeline([{clipInfo}])` | `Bool` | Keys: `mediaPoolItem`, `startFrame`, `endFrame` |
| `CreateTimelineFromClips(name, [clips])` | `Timeline` | |
| `ImportTimelineFromFile(filePath, {options})` | `Timeline` | Accepts EDL, XML, AAF, FCPXML, DRT, OTIO, ADL |

#### Folder
| Method | Returns |
|---|---|
| `GetName()` | `string` |
| `GetClipList()` | `[MediaPoolItem]` |
| `GetSubFolderList()` | `[Folder]` |

#### MediaPoolItem
| Method | Returns | Notes |
|---|---|---|
| `GetMetadata(type)` | `{metadata}` | No arg = all metadata |
| `SetMetadata(type, value)` | `Bool` | |
| `GetMediaId()` | `string` | Unique ID |
| `GetClipProperty(key)` | `{props}` | No arg = all properties |
| `SetClipProperty(key, val)` | `Bool` | |
| `GetClipColor()` / `SetClipColor(name)` / `ClearClipColor()` | | |
| `AddMarker(frameId, color, name, note, duration, customData)` | `Bool` | `customData` accepts arbitrary string (e.g. JSON for structured QC data) |
| `GetMarkers()` | `{frameId→{color,duration,note,name,customData}}` | |
| `DeleteMarkersByColor(color)` | `Bool` | `"All"` deletes all |
| `DeleteMarkerAtFrame(frameNum)` | `Bool` | |
| `AddFlag(color)` / `GetFlagList()` / `ClearFlags(color)` | | |

#### Timeline
| Method | Returns | Notes |
|---|---|---|
| `GetName()` / `SetName(name)` | | |
| `GetStartFrame()` / `GetEndFrame()` | `int` | |
| `GetTrackCount(type)` | `int` | `"video"`, `"audio"`, `"subtitle"` |
| `GetItemListInTrack(type, idx)` | `[TimelineItem]` | 1-based |
| `GetTrackName(type, idx)` / `SetTrackName(type, idx, name)` | | |
| `GetCurrentTimecode()` | `string` | Works on Cut, Edit, Color, Deliver pages |
| `GetCurrentVideoItem()` | `TimelineItem` | |
| `AddMarker(...)` / `GetMarkers()` / `DeleteMarkersByColor(color)` | | Same as MediaPoolItem |
| `ApplyGradeFromDRX(path, gradeMode, [items])` | `Bool` | gradeMode: 0=no KF, 1=src TC aligned, 2=start frames aligned |
| `GetCurrentClipThumbnailImage()` | `{width,height,format,data}` | Base64 RGB8 — Color page only |

#### TimelineItem
| Method | Returns | Notes |
|---|---|---|
| `GetName()` / `GetDuration()` / `GetStart()` / `GetEnd()` | | |
| `GetLeftOffset()` / `GetRightOffset()` | `int` | Max trim frames available |
| `GetMediaPoolItem()` | `MediaPoolItem` | |
| `GetFusionCompCount()` | `int` | |
| `GetFusionCompByIndex(idx)` / `GetFusionCompByName(name)` | `fusionComp` | |
| `GetFusionCompNameList()` | `[names]` | |
| `AddFusionComp()` / `ImportFusionComp(path)` / `ExportFusionComp(path, idx)` | | |
| `DeleteFusionCompByName(name)` / `LoadFusionCompByName(name)` | | |
| `AddVersion(name, type)` / `LoadVersionByName(name, type)` | | type: 0=local, 1=remote |
| `SetLUT(nodeIndex, lutPath)` | `Bool` | 1-based nodeIndex (changed from 0-based in v16.2.0) |
| `SetCDL({NodeIndex, Slope, Offset, Power, Saturation})` | `Bool` | |
| `CopyGrades([targetItems])` | `Bool` | |
| `AddTake(item, startFrame, endFrame)` / `FinalizeTake()` | | |
| `AddMarker(...)` / `GetMarkers()` / `DeleteMarkersByColor(color)` | | Same structure |
| `GetClipColor()` / `SetClipColor(name)` / `ClearClipColor()` | | |

### Markers — Structured Data Pattern

The `customData` field on markers accepts any string. Encoding JSON enables structured metadata on any frame of any clip, timeline, or timeline item — useful for QC categories, severity, reviewer names, or external tool references:

```python
import json
item.AddMarker(
    frameId=96,
    color="Red",
    name="QC Fail",
    note="Clipped audio",
    duration=1,
    customData=json.dumps({"severity": "critical", "reviewer": "jsmith", "category": "audio"})
)

markers = item.GetMarkers()
for frame, m in markers.items():
    data = json.loads(m.get("customData", "{}"))
    print(frame, data)
```

---

## What the API Can and Cannot Do

### Can do
- Full project lifecycle (create, load, save, close, export, archive, restore)
- Database switching (disk and PostgreSQL), cloud project ops
- Media pool: import, organize bins, relink, proxies, full metadata R/W
- Timeline import from EDL, XML, AAF, FCPXML, DRT, OTIO, ADL
- Track management: add, delete, enable, lock, rename (video/audio/subtitle/Atmos adaptive)
- Markers with custom JSON payloads on clips, timelines, and timeline items
- Color page: apply LUTs per node, read/write CDL values per node, apply `.drx` grades, copy grades, export cube LUTs, manage gallery stills/albums
- Full render queue scripting: add/delete jobs, start/stop, query progress, configure every render parameter, load/save presets
- Scene cut detection trigger, audio transcription trigger, Magic Mask creation trigger

### Cannot do
- Timeline editing: no cut, split, trim, move, reorder clips, transitions, fades, speed changes, retiming
- Color page: primary wheels, curves, qualifiers, power windows, HDR palette, OFX plugins — all inaccessible
- Node graph: cannot create, delete, reorder, or inspect color nodes via script
- Fairlight: mixer, EQ, dynamics, bus routing, audio automation, fades, recording
- Smart Bins: cannot be created via script (writing metadata populates them indirectly)
- OFX plugins: invisible on all pages
- AI features: SuperScale, Dialogue Matcher, AI Audio Assistant, Facial Recognition, generative AI — not accessible; only Magic Mask creation, transcription trigger, and voice isolation state are exposed
- Render presets: cannot be created from scratch via API — must be created manually in Deliver page first, then can be loaded/applied programmatically

---

## Known Bugs and Version Notes

- `fu.GetCurrentComp()` returns `None` unless the Fusion page has been visited at least once in the current session → workaround: call `resolve.OpenPage("fusion")` before accessing compositions.
- The first `AddRenderJob()` in a new project can fail silently → add a retry loop or short delay.
- Windows: Python 3.11+ can cause segfaults with `fusionscript.dll` → use Python 3.10.
- Windows: env var paths must not include quotation marks (despite official docs showing them).
- Resolve 18.5 Beta 3 disabled all undocumented API methods without notice. Any automation on undocumented calls is fragile — test on every Resolve update.
- `SetLUT()` / `SetCDL()` `nodeIndex` is **1-based** from v16.2.0 onwards (was 0-based before).

---

## Workflow Integrations (Studio only)

Workflow Integration plugins are Electron apps that load inside Resolve under **Workspace > Workflow Integrations**. More than one plugin can be active simultaneously.

For technical details and sample code: **Help > Documentation > Developer > Workflow Integrations folder** inside Resolve.

### File structure

```
MyPlugin/
├── package.json        # name, version, main entry
├── index.html          # panel UI
├── index.js            # Electron renderer
└── scripts/
    └── helper.py       # optional Python/Lua scripts
```

`package.json` minimum:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "main": "index.js",
  "resolve": { "name": "My Plugin Display Name" }
}
```

### JS ↔ Resolve bridge

```js
const resolve = require('davinci-resolve');
const project = resolve.GetProjectManager().GetCurrentProject();
console.log(project.GetName());
```

Install location:
- macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Workflow Integration Plugins/`
- Windows: `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Workflow Integration Plugins\`

---

## Fusion Fuse Plugins

A Fuse is a `.fuse` Lua file defining a custom Fusion tool, scanned from the `Fuses/` directory on startup. Fuses hot-reload via **Script > Reload** without restarting Resolve.

### Minimal Fuse skeleton

```lua
FuRegisterClass("MyEffect", CT_Tool, {
  REGS_Name        = "My Effect",
  REGS_Category    = "My Plugins",
  REGS_OpDescription = "Does something",
  REG_NoMotionBlurCtrls = true,
})

function Create()
  InImage  = self:AddInput("Input",  "Input",  { LINKID_DataType = "Image", LINK_Main = 1 })
  OutImage = self:AddOutput("Output", "Output", { LINKID_DataType = "Image", LINK_Main = 1 })
  InSlider = self:AddInput("Strength", "Strength", {
    LINKID_DataType    = "Number",
    INPID_InputControl = "SliderControl",
    INP_Default = 0.5, INP_MinAllowed = 0.0, INP_MaxAllowed = 1.0,
  })
end

function Process(req)
  local img = InImage:GetValue(req)
  -- pixel processing here
  OutImage:Set(req, img)
end
```

### Fuse install paths

- macOS: `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses/`
- Windows: `%APPDATA%\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses\`

### Reactor

Reactor is a **community package manager** (not an SDK) for Fusion/Resolve tools — fuses, scripts, macros. Install via the bootstrap script at [www.steakunderwater.com](https://www.steakunderwater.com). Use it to discover and install community tools, not for building your own.

---

## Python Libraries and Ecosystem Tools

| Tool | Type | Notes |
|---|---|---|
| `pydavinci` | Typed Python wrapper | IDE auto-completion, surfaces errors before execution |
| `pybmd` | Python wrapper | Similar to pydavinci, available on PyPI |
| `davinci-resolve-mcp` | MCP integration | Connects Claude/Cursor/VS Code Copilot to a live Resolve instance via Model Context Protocol; exposes all 324 API methods as structured tools — prevents LLM hallucination of nonexistent methods. [github.com/samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) |
| `auto-subs` | Community script | AI subtitle generation with direct Resolve placement |
| `StoryToolkitAI` | Community tool | Whisper transcription + semantic footage search integrated with Resolve |
| `davinci-resolve-postgresql-workflow-tools` | Community tool | Automated PostgreSQL database backup and optimisation |
| `opentimelineio` | Python lib | Timeline interchange format (useful for import/export scripting) |

> **LLM + Resolve scripts**: LLMs hallucinate nonexistent Resolve methods. Paste the full scripting README (~15–20 KB) as context and restrict generation to documented methods only. The `davinci-resolve-mcp` project is the most complete mitigation.

---

## Official Documentation Sources

Always start with the docs shipped inside Resolve (they match the exact installed version).

| Resource | Location / URL |
|---|---|
| Scripting README (official, shipped) | Inside Resolve: **Help > Documentation > Developer** |
| Scripting examples (shipped) | See paths under "Running Scripts" above |
| Workflow Integrations sample code | **Help > Documentation > Developer > Workflow Integrations folder** |
| Fusion SDK PDF (official) | https://documents.blackmagicdesign.com/UserManuals/Fusion_Fuse_SDK.pdf |
| Scripting API mirror — X-Raym v20.3 | https://gist.github.com/X-Raym/2f2bf453fc481b9cca624d7ca0e19de8 |
| Formatted scripting docs — X-Raym | https://www.extremraym.com/en/resolve-api-doc-release/ |
| Unofficial API docs (deric mirror) | https://deric.github.io/DaVinciResolve-API-Docs/ |
| ResolveDevDoc (ReadTheDocs) | https://resolvedevdoc.readthedocs.io |
| Workflow Integrations detail (VFXPedia) | https://www.steakunderwater.com/VFXPedia/__man/Resolve18-6/DaVinciResolve18_Manual_files/part4123.htm |
| Wild Lion Media scripting guide | https://wildlion.media/davinci-resolve-python-scripting-the-complete-guide-to-the-api/ |
| We Suck Less / Steak Under Water forum | https://www.steakunderwater.com (225+ scripting topics) |
| Blackmagic Design forum scripting | https://forum.blackmagicdesign.com (scripting subforum) |

Unofficial mirrors may lag or contain errors — the shipped README is always authoritative.

---

## Key Caveats

- The API is **almost entirely silent on failure** — methods return `False`/`None` without error messages. Check every return value. Defensive coding is mandatory, not optional.
- The API is **synchronous and single-threaded** — do not block the Resolve UI thread with long operations.
- API coverage of Resolve's full feature set is approximately **30–40%**. Build automation around proven strengths: delivery, project management, media operations, metadata, and markers.
- Blackmagic has broken undocumented API methods without notice (Resolve 18.5 Beta 3 disabled all of them). Treat undocumented calls as fragile.
- Render presets cannot be created from scratch via API — create them manually in the Deliver page first.
- Smart Bins cannot be created via script.
