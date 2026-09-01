import os

from libqtile import bar, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
import subprocess

# Check qtile version: apt policy qtile

mod = "mod4"
terminal = "kitty"
os.environ["GTK_THEME"] = 'Adwaita:dark'

layout_theme = {
    "border_focus": "#ff0",
    "border_normal": "#220",
    "border_width": 4,
    "margin": 10
}


def network_status():
    try:
        output = subprocess.check_output(
            [
                "nmcli",
                "-t",
                "-f",
                "TYPE,STATE,CONNECTION",
                "device"
            ],
            text=True
        )

        for line in output.splitlines():
            dev_type, state, connection = line.split(":", 2)
            if state == "connected":
                if dev_type == "wifi":
                    return f"🛜 {connection}"
                elif dev_type == "Ethernet":
                    return f"🖧 {connection}"

        return "🚫 Offline"

    except Exception:
        return "?"


keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(),
        desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.shuffle_left(),
        desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right(),
        desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(),
        desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    Key([mod, "control"], "h", lazy.layout.grow_left(),
        desc="Grow window to the left"),
    Key([mod, "control"], "l", lazy.layout.grow_right(),
        desc="Grow window to the right"),
    Key([mod, "control"], "j", lazy.layout.grow_down(),
        desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(),
        desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    ####
    #   Launch programs
    ####
    Key(
        [mod], "e",
        lazy.spawn("thunar"),
        desc="Thunar file explorer"
    ),
    Key(
        [mod], "r",
        lazy.spawn("rofi -show run -show-icons"),
        desc="Rofi run mode"
    ),
    Key(
        [mod, "shift"], "r",
        lazy.spawn("rofi -show drun -show-icons"),
        desc="Rofi drun mode"
    ),
    Key(
        [mod], "b",
        lazy.spawn("firefox"),
        desc="Firefox web browser"
    ),
    ####
    #   Other system controls
    ####
    Key(
        [], "XF86AudioRaiseVolume",
        lazy.spawn("/home/jordan/.config/qtile/volume.sh up"),
        desc="Increase volume level"
    ),
    Key(
        [], "XF86AudioLowerVolume",
        lazy.spawn("/home/jordan/.config/qtile/volume.sh down"),
        desc="Decrease volume level"
    ),
    Key(
        [], "XF86AudioMute",
        lazy.spawn("pamixer --toggle-mute"),
        desc="Mute volume"
    ),
    Key(
        [], "XF86MonBrightnessUp",
        lazy.spawn("brightnessctl set 5%+"),
        desc="Increase brightness"
    ),
    Key(
        [], "XF86MonBrightnessDown",
        lazy.spawn("brightnessctl set 5%-"),
        desc="Decrease brightness"
    ),
    Key(
        [mod], "L",
        lazy.spawn("i3lock"),
        desc="Lock screen"
    )
]

"""
Add key bindings to switch VTs in Wayland.

We can't check qtile.core.name in default config,
    as it is loaded before qtile is started

We therefore defer the check until the key binding is run by using:
    .when(func=...)
"""
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(
                func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


groups = [Group(i) for i in "12345"]

for i in groups:
    keys.extend(
        [
            # mod + group number = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc=f"Switch to group {i.name}",
            ),
            # mod + shift + group number =
            #   switch to & move focused window to group
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
                desc=f"Switch to & move focused window to group {i.name}",
            ),
            # Or, use below if you prefer not to switch to that group.
            # # mod + shift + group number = move focused window to group
            # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
            #     desc="move focused window to group {}".format(i.name)),
        ]
    )

layouts = [
    layout.Columns(**layout_theme),
    layout.Max(**layout_theme),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.TreeTab(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
]

widget_defaults = dict(
    font="sans bold",
    fontsize=12,
    padding=12,
    foreground="#fff"
)
extension_defaults = widget_defaults.copy()

screens = [
    Screen(
        top=bar.Bar(
            [
                widget.CurrentLayout(),
                widget.GroupBox(padding=5),
                widget.Prompt(),
                widget.WindowName(),
                widget.Chord(
                    chords_colors={
                        "launch": ("#ff0000", "#ffffff"),
                    },
                    name_transform=lambda name: name.upper(),
                ),
                widget.Pomodoro(update_interval=0.25),
                widget.Battery(
                    charging_background="#0a0",
                    charging_foreground="#000",
                    low_background="#f00",
                    low_foreground="#fff",
                    low_percentage=0.25,
                    format="🔌 {percent:2.0%}",
                    update_interval=30
                ),
                widget.Volume(
                    get_volume_command="pamixer --get-volume-human",
                    mute_format="🔊 Mute",
                    unmute_format="🔊 {volume}%"
                ),
                widget.GenPollText(
                    func=network_status,
                    update_interval=5
                ),
                widget.Systray(),  # Use widget.StatusNotifier on wayland
                widget.Clock(format="%a %d/%m/%Y %H:%M"),
            ],
            24,
        ),
        background="#000000",
        wallpaper_mode="center",
        # You can uncomment this variable if you see that on X11
        #    floating resize/moving is laggy
        # By default we handle these events delayed to already improve
        #    performance, however your system might still be struggling
        # This variable is set to None (no cap) by default, but you can set it
        #    to 60 to indicate that you limit it to 60 events per second
        # x11_drag_polling_rate = 60,
    ),
]

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(),
         start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(),
         start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class & name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
focus_previous_on_window_remove = False
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

idle_inhibitors = []  # type: list

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
