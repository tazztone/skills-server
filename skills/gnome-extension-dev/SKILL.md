---
name: gnome-extension-dev
description: "Build and debug GNOME Shell extensions in GJS. Use when: creating a new extension, adding panel/quick-settings UI, implementing GTK4 preferences, debugging in a nested session, porting across GNOME versions, or preparing for extensions.gnome.org submission."
---

# GNOME Shell Extensions

Build extensions for GNOME Shell 45+ using GJS with ESModules.

## Leading Concepts

**Cleanup contract** — Everything created in `enable()` MUST be undone in `disable()`. This is the core invariant enforced by review.

**Process boundary** — `extension.js` runs inside `gnome-shell` (Clutter/St, no GTK). `prefs.js` runs separately (GTK4/Adwaita, no Shell APIs).

**Injection** — Override Shell methods via `InjectionManager`; always clear in `disable()`.

## Architecture

### Library Stack (bottom-up)

| Layer | Purpose |
|-------|---------|
| Clutter | Actor-based toolkit, layout, animations |
| St | Shell widgets: buttons, icons, labels (CSS-styleable) |
| Meta (Mutter) | Displays, workspaces, windows, keybindings |
| Shell | `global` object, app tracking, utilities |
| js/ui/ | GNOME Shell modules (Main, Panel, PopupMenu, QuickSettings) |

### Import Conventions

**extension.js**:
```js
import Clutter from "gi://Clutter";
import GObject from "gi://GObject";
import Gio from "gi://Gio";
import GLib from "gi://GLib";
import Meta from "gi://Meta";
import Shell from "gi://Shell";
import St from "gi://St";

import { Extension, gettext as _ } from "resource:///org/gnome/shell/extensions/extension.js";
import * as Main from "resource:///org/gnome/shell/ui/main.js";
import * as PanelMenu from "resource:///org/gnome/shell/ui/panelMenu.js";
import * as PopupMenu from "resource:///org/gnome/shell/ui/popupMenu.js";
import * as QuickSettings from "resource:///org/gnome/shell/ui/quickSettings.js";
```

**prefs.js**:
```js
import Gdk from "gi://Gdk?version=4.0";
import Gtk from "gi://Gtk?version=4.0";
import Adw from "gi://Adw";
import Gio from "gi://Gio";

import { ExtensionPreferences, gettext as _ } from "resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js";
```

**Rule**: Never import GTK/Gdk/Adw in `extension.js`. Never import Clutter/Meta/St/Shell in `prefs.js`.

## File Structure

### Required
- **`metadata.json`** — UUID, name, description, shell-version, url
- **`extension.js`** — Default export: subclass of `Extension`

### Optional
- **`prefs.js`** — Subclass of `ExtensionPreferences` (GTK4/Adwaita)
- **`stylesheet.css`** — CSS for St widgets (extension process only)
- **`schemas/`** — GSettings schema XML + compiled binary (`glib-compile-schemas`)
- **`locale/`** — Gettext .mo files

### metadata.json Template
```json
{
  "uuid": "my-extension@example.com",
  "name": "My Extension",
  "description": "Does something useful",
  "shell-version": ["47", "48", "49"],
  "url": "https://github.com/user/my-extension"
}
```

## Lifecycle: enable()/disable()

```js
import { Extension } from "resource:///org/gnome/shell/extensions/extension.js";

export default class MyExtension extends Extension {
  enable() {
    // Create objects, connect signals, add UI
  }

  disable() {
    // Undo everything from enable():
    // - Destroy all widgets
    // - Disconnect all signals
    // - Remove all GLib.timeout/idle sources
    // - Null all references
  }
}
```

**Rules**:
- Do NOT create GObject instances or connect signals in `constructor()`
- `constructor()` only sets static data (RegExp, Map) and calls `super(metadata)`
- `disable()` is called on lock screen (unless `session-modes` includes `unlock-dialog`)

## Branches

### Branch: Create New Extension

1. **Create file structure** — `metadata.json`, `extension.js`, optional `prefs.js`, `stylesheet.css`, `schemas/`
2. **Implement enable()/disable()** — Follow cleanup contract; track all created objects/signals/sources
3. **Test in nested session**:
   ```sh
   # GNOME 49+
   dbus-run-session gnome-shell --devkit --wayland
   # GNOME 48 and earlier
   dbus-run-session gnome-shell --nested --wayland
   
   # In nested session
   gnome-extensions enable my-extension@example.com
   journalctl -f -o cat /usr/bin/gnome-shell
   ```
4. **Verify cleanup** — Disable/re-enable repeatedly; watch for memory leaks or orphaned UI

**Completion**: Extension loads without error, UI appears, disable() fully cleans up, logs show no warnings.

### Branch: Add Panel Indicator

```js
import St from "gi://St";
import { Extension } from "resource:///org/gnome/shell/extensions/extension.js";
import * as Main from "resource:///org/gnome/shell/ui/main.js";
import * as PanelMenu from "resource:///org/gnome/shell/ui/panelMenu.js";

export default class MyExtension extends Extension {
  enable() {
    this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);
    
    const icon = new St.Icon({
      icon_name: "face-laugh-symbolic",
      style_class: "system-status-icon",
    });
    this._indicator.add_child(icon);
    
    Main.panel.addToStatusArea(this.uuid, this._indicator);
  }

  disable() {
    this._indicator?.destroy();
    this._indicator = null;
  }
}
```

**Completion**: Icon visible in panel, clicks respond, icon removed on disable.

### Branch: Add Quick Settings Toggle

```js
import { Extension } from "resource:///org/gnome/shell/extensions/extension.js";
import * as QuickSettings from "resource:///org/gnome/shell/ui/quickSettings.js";
import * as PopupMenu from "resource:///org/gnome/shell/ui/popupMenu.js";

export default class MyExtension extends Extension {
  enable() {
    this._toggle = new QuickSettings.MenuToggle({
      title: "My Toggle",
      icon_name: "face-laugh-symbolic",
      toggleMode: true,
    });
    this._toggle.connect("notify::checked", () => {
      console.log("Toggle:", this._toggle.checked);
    });
    QuickSettings.systemMenu._addItems(this._toggle);
  }

  disable() {
    this._toggle?.destroy();
    this._toggle = null;
  }
}
```

**Completion**: Toggle appears in Quick Settings, state changes logged, destroyed on disable.

### Branch: Add Popup Menu to Panel

```js
import St from "gi://St";
import { Extension } from "resource:///org/gnome/shell/extensions/extension.js";
import * as Main from "resource:///org/gnome/shell/ui/main.js";
import * as PanelMenu from "resource:///org/gnome/shell/ui/panelMenu.js";
import * as PopupMenu from "resource:///org/gnome/shell/ui/popupMenu.js";

export default class MyExtension extends Extension {
  enable() {
    this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);
    
    const icon = new St.Icon({
      icon_name: "face-laugh-symbolic",
      style_class: "system-status-icon",
    });
    this._indicator.add_child(icon);
    
    // Add menu item
    const item = new PopupMenu.PopupMenuItem("Click me");
    item.connect("activate", () => console.log("Activated!"));
    this._indicator.menu.addItem(item);
    
    Main.panel.addToStatusArea(this.uuid, this._indicator);
  }

  disable() {
    this._indicator?.destroy();
    this._indicator = null;
  }
}
```

**Completion**: Panel icon with dropdown menu, items activate, menu destroyed on disable.

### Branch: Implement Preferences (GTK4/Adwaita)

**prefs.js**:
```js
import Gtk from "gi://Gtk?version=4.0";
import Adw from "gi://Adw";
import Gio from "gi://Gio";
import { ExtensionPreferences, gettext as _ } from "resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js";

export default class MyPrefs extends ExtensionPreferences {
  fillPreferencesWindow(window) {
    const page = new Adw.PreferencesPage();
    const group = new Adw.PreferencesGroup({ title: "Settings" });
    page.add(group);

    const row = new Adw.ActionRow({ title: "Show indicator" });
    const toggle = new Gtk.Switch({
      valign: Gtk.Align.CENTER,
    });
    row.add_suffix(toggle);
    row.activatable_widget = toggle;
    
    // Bind to GSettings
    this._settings = this.getSettings();
    this._settings.bind("show-indicator", toggle, "active", Gio.SettingsBindFlags.DEFAULT);
    
    group.add(row);
    page.add(group);
    window.add(page);
  }
}
```

**schemas/gschemas.compiled** — Generate with `glib-compile-schemas schemas/`

**Completion**: Preferences dialog opens from extensions.gnome.org or gnome-tweaks, toggles persist across restarts.

### Branch: Debug Extension

1. **Run nested session** — Isolate from main session
2. **Watch logs**:
   ```sh
   journalctl -f -o cat /usr/bin/gnome-shell
   ```
3. **Reload without restart**:
   ```sh
   # GNOME 45+
   dbus-send --print-reply --dest=org.gnome.Shell /org/gnome/Shell org.gnome.Shell.Eval string:"Main.extensionManager.enableExtension('my-extension@example.com')"
   ```
4. **Check common issues**:
   - Missing cleanup (memory leak on disable/enable cycles)
   - Signal leaks (disconnect in disable())
   - Source leaks (`GLib.Source.remove()` in disable())
   - Import errors (wrong GI version, cross-process imports)

**Completion**: Issue identified, fix applied, verified in fresh nested session.

### Branch: Port to New GNOME Version

1. **Check breaking changes** — Review GNOME Shell release notes for 45-49
2. **Update `shell-version`** in metadata.json
3. **Test each feature** — Panel, Quick Settings, PopupMenu APIs shift frequently
4. **Fix deprecated patterns**:
   - GNOME 45: ESModules required, `init()` removed
   - GNOME 47: Quick Settings changes
   - GNOME 48+: Panel API shifts
5. **Verify in nested session** for each target version

**Completion**: Extension loads on target version, all features functional, no deprecation warnings.

### Branch: Prepare for Submission

1. **Review compliance**:
   - No external dependencies
   - All created objects destroyed in disable()
   - All signals disconnected
   - All sources removed
   - No GTK imports in extension.js
   - Proper error handling
2. **Package**:
   ```sh
   cd ~/.local/share/gnome-shell/extensions/my-extension@example.com
   gnome-extensions pack --podir=po --extra-source=utils.js .
   ```
3. **Upload** (GNOME 49+):
   ```sh
   gnome-extensions upload --accept-tos
   ```
4. **Or upload manually** — https://extensions.gnome.org/upload/

**Completion**: Extension packaged, uploaded, passes automated review.

## Common Patterns

### Signal Connection (with cleanup)
```js
enable() {
  this._handlerId = someObject.connect('some-signal', () => { /* ... */ });
}
disable() {
  if (this._handlerId) {
    someObject.disconnect(this._handlerId);
    this._handlerId = null;
  }
}
```

### Timeout (with cleanup)
```js
enable() {
  this._timeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 5, () => {
    // do work
    return GLib.SOURCE_CONTINUE;
  });
}
disable() {
  if (this._timeoutId) {
    GLib.Source.remove(this._timeoutId);
    this._timeoutId = null;
  }
}
```

### GSettings Binding
```js
enable() {
  this._settings = this.getSettings();
  this._settings.bind('show-indicator', this._indicator, 'visible', Gio.SettingsBindFlags.DEFAULT);
}
disable() {
  this._settings = null;
}
```

### Method Override (InjectionManager)
```js
import { Extension, InjectionManager } from "resource:///org/gnome/shell/extensions/extension.js";
import { Panel } from "resource:///org/gnome/shell/ui/panel.js";

export default class MyExtension extends Extension {
  enable() {
    this._injectionManager = new InjectionManager();
    this._injectionManager.overrideMethod(
      Panel.prototype,
      "toggleCalendar",
      (originalMethod) => {
        return function (...args) {
          console.debug("Calendar toggled!");
          originalMethod.call(this, ...args);
        };
      },
    );
  }
  disable() {
    this._injectionManager.clear();
    this._injectionManager = null;
  }
}
```

## Key Resources

- **GJS API Docs**: https://gjs-docs.gnome.org/
- **GNOME Shell Source**: https://gitlab.gnome.org/GNOME/gnome-shell/-/tree/main/js/ui
- **Extensions Guide**: https://gjs.guide/extensions/
- **Review Guidelines**: https://gjs.guide/extensions/review-guidelines/review-guidelines.html