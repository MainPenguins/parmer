import Clutter from 'gi://Clutter';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Shell from 'gi://Shell';
import St from 'gi://St';

import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';

const IFACE = 'dev.parmer.Overlay';
const OBJECT_PATH = '/dev/parmer/Overlay';
const SIGNAL_NAME = 'ShowRequested';
const APPLY_SIGNAL_NAME = 'ApplyRequested';

export default class ParmerOverlayExtension extends Extension {
    enable() {
        this._overlay = new St.BoxLayout({
            vertical: true,
            style:
                'background-color: rgba(24, 24, 24, 0.92);' +
                'border-radius: 12px;' +
                'padding: 10px 14px;',
        });

        this._clickProbeId = global.stage.connect('captured-event', (actor, event) => {
            if (!this._overlay || !this._overlay.visible) {
                return Clutter.EVENT_PROPAGATE;
            }

            const type = event.type();

            if (
                type === Clutter.EventType.BUTTON_PRESS ||
                type === Clutter.EventType.BUTTON_RELEASE
            ) {
                const [x, y] = event.get_coords();

                console.log(`parmer overlay: raw ${type} at ${x},${y}`);
            }

            return Clutter.EVENT_PROPAGATE;
        });

        console.log(
            `parmer overlay: API probe stage=${!!global.stage} display=${!!global.display} pointer=${typeof global.get_pointer}`
        );

        const candidates = [
            ['Main.ui_group', Main.ui_group],
            ['Main.layoutManager.uiGroup', Main.layoutManager && Main.layoutManager.uiGroup],
            ['Main.layout.layoutGroup', Main.layout && Main.layout.layoutGroup],
        ];

        let chosen = null;
        let chosenName = '';

        for (const [name, actor] of candidates) {
            if (actor && typeof actor.add_child === 'function') {
                chosen = actor;
                chosenName = name;
                break;
            }
        }

        if (!chosen) {
            chosen = global.stage;
            chosenName = 'global.stage';
        }

        console.log(`parmer overlay: parent = ${chosenName}`);

        this._parent = chosen;

        this._parent.add_child(this._overlay);

        this._hide();

        try {
            this._focusSignalId = global.display.connect(
                'focus-window',
                () => this._hide()
            );
        } catch (e) {
            console.log('parmer overlay: focus tracking unavailable');
        }

        this._signalId = Gio.DBus.session.signal_subscribe(
            null,
            IFACE,
            SIGNAL_NAME,
            OBJECT_PATH,
            null,
            Gio.DBusSignalFlags.NONE,
            (connection, sender, path, iface, member, params) => {
                const application = params.get_child_value(0).get_string()[0];
                const lines = params.get_child_value(1).get_strv();

                console.log(`parmer overlay: show requested for ${application}`);

                this._show(application, lines);
            }
        );

        console.log(`parmer overlay: enabled, subscription id ${this._signalId}`);

        Main.wm.setCustomKeybindingHandler(
            'move-to-center',
            Shell.ActionMode.ALL,
            () => this._applyTop()
        );

        const selfTest = new GLib.Variant('(sas)', ['Self Test', ['self -> test']]);

        Gio.DBus.session.emit_signal(
            null,
            OBJECT_PATH,
            IFACE,
            SIGNAL_NAME,
            selfTest
        );
    }

    disable() {
        this._clearTimer();

        Main.wm.setCustomKeybindingHandler(
            'move-to-center',
            Shell.ActionMode.ALL,
            null
        );

        if (this._clickProbeId) {
            global.stage.disconnect(this._clickProbeId);
            this._clickProbeId = null;
        }

        if (this._focusSignalId) {
            try {
                global.display.disconnect(this._focusSignalId);
            } catch (e) {
            }

            this._focusSignalId = null;
        }

        if (this._signalId) {
            Gio.DBus.session.signal_unsubscribe(this._signalId);
            this._signalId = null;
        }

        if (this._overlay && this._parent && this._overlay.get_parent() === this._parent) {
            this._parent.remove_child(this._overlay);
        }

        if (this._overlay) {
            this._overlay.destroy();
            this._overlay = null;
        }
    }

    _applyTop() {
        console.log('parmer overlay: shortcut apply');

        const params = new GLib.Variant('(i)', [0]);

        Gio.DBus.session.emit_signal(
            null,
            OBJECT_PATH,
            IFACE,
            APPLY_SIGNAL_NAME,
            params
        );

        this._hide();
    }

    _show(application, lines) {
        this._clearTimer();

        this._overlay.destroy_all_children();

        this._overlay.add_child(
            new St.Label({
                text: application,
                style: 'font-weight: bold; color: #f6f6f5; margin-bottom: 6px;',
            })
        );

        for (let index = 0; index < lines.length; index++) {
            const rowContent = new St.BoxLayout({ vertical: false });

            const label = new St.Label({
                text: lines[index],
                style: 'color: #c0bfbc; margin-right: 12px;',
            });

            const applyLabel = new St.Label({
                text: 'apply',
                style: 'color: #8bff9c; font-weight: bold;',
            });

            rowContent.add_child(label);
            rowContent.add_child(applyLabel);

            const row = new St.Button({
                child: rowContent,
                reactive: true,
                style: 'padding: 4px 6px;',
            });

            row.connect('clicked', () => {
                console.log(`parmer overlay: clicked ${index}`);

                const params = new GLib.Variant('(i)', [index]);

                Gio.DBus.session.emit_signal(
                    null,
                    OBJECT_PATH,
                    IFACE,
                    APPLY_SIGNAL_NAME,
                    params
                );

                this._hide();
            });

            this._overlay.add_child(row);
        }

        this._overlay.show();

        if (typeof this._overlay.raise_top === 'function') {
            this._overlay.raise_top();
        }

        this._reposition();

        const [showX, showY] = this._overlay.get_position();

        console.log(`parmer overlay: shown at ${showX},${showY}`);

        this._timerId = GLib.timeout_add_seconds(
            GLib.PRIORITY_DEFAULT,
            8,
            () => {
                this._hide();
                return GLib.SOURCE_REMOVE;
            }
        );
    }

    _reposition() {
        let pointerX = 0;
        let pointerY = 0;

        try {
            [pointerX, pointerY] = global.get_pointer();
        } catch (e) {
        }

        let width = this._overlay.width;
        let height = this._overlay.height;

        if (!Number.isFinite(width) || width <= 0) {
            width = 240;
        }

        if (!Number.isFinite(height) || height <= 0) {
            height = 80;
        }

        let stageWidth = global.stage.get_width();
        let stageHeight = global.stage.get_height();

        if (!Number.isFinite(stageWidth) || stageWidth <= 300) {
            stageWidth = 1920;
        }

        if (!Number.isFinite(stageHeight) || stageHeight <= 300) {
            stageHeight = 1080;
        }

        let x = pointerX - width / 2;
        x = Math.max(8, Math.min(x, stageWidth - width - 8));

        let y = pointerY - height - 14;

        if (y < 8) {
            y = pointerY + 24;
        }

        y = Math.max(8, Math.min(y, stageHeight - height - 8));

        if (!Number.isFinite(x)) {
            x = 40;
        }

        if (!Number.isFinite(y)) {
            y = 40;
        }

        this._overlay.set_position(Math.round(x), Math.round(y));
    }

    _hide() {
        this._clearTimer();

        if (this._overlay) {
            this._overlay.hide();
        }
    }

    _clearTimer() {
        if (this._timerId) {
            GLib.Source.remove(this._timerId);
            this._timerId = null;
        }
    }
}
