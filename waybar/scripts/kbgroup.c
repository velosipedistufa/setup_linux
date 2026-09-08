/* Print current wl_keyboard xkb group as en/ru JSON lines for waybar.
 * Group 0 = us (shown en), group 1 = ru. No dwl patch. */
#define _POSIX_C_SOURCE 200809L
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wayland-client.h>

static struct wl_seat *seat;
static struct wl_keyboard *keyboard;
static uint32_t last_group = UINT32_MAX;

static const char *
label(uint32_t group)
{
	switch (group) {
	case 0:
		return "en";
	case 1:
		return "ru";
	default:
		return "??";
	}
}

static void
emit(uint32_t group)
{
	const char *l;

	if (group == last_group)
		return;
	last_group = group;
	l = label(group);
	printf("{\"text\":\"%s\",\"class\":\"%s\",\"tooltip\":\"layout %s\"}\n",
	       l, l, l);
	fflush(stdout);
}

static void
kb_keymap(void *data, struct wl_keyboard *kb, uint32_t format, int32_t fd,
          uint32_t size)
{
	(void)data;
	(void)kb;
	(void)format;
	(void)size;
	if (fd >= 0)
		close(fd);
}

static void
kb_enter(void *data, struct wl_keyboard *kb, uint32_t serial,
         struct wl_surface *surface, struct wl_array *keys)
{
	(void)data;
	(void)kb;
	(void)serial;
	(void)surface;
	(void)keys;
}

static void
kb_leave(void *data, struct wl_keyboard *kb, uint32_t serial,
         struct wl_surface *surface)
{
	(void)data;
	(void)kb;
	(void)serial;
	(void)surface;
}

static void
kb_key(void *data, struct wl_keyboard *kb, uint32_t serial, uint32_t time,
       uint32_t key, uint32_t state)
{
	(void)data;
	(void)kb;
	(void)serial;
	(void)time;
	(void)key;
	(void)state;
}

static void
kb_modifiers(void *data, struct wl_keyboard *kb, uint32_t serial,
             uint32_t mods_depressed, uint32_t mods_latched,
             uint32_t mods_locked, uint32_t group)
{
	(void)data;
	(void)kb;
	(void)serial;
	(void)mods_depressed;
	(void)mods_latched;
	(void)mods_locked;
	emit(group);
}

static void
kb_repeat(void *data, struct wl_keyboard *kb, int32_t rate, int32_t delay)
{
	(void)data;
	(void)kb;
	(void)rate;
	(void)delay;
}

static const struct wl_keyboard_listener kb_listener = {
	.keymap = kb_keymap,
	.enter = kb_enter,
	.leave = kb_leave,
	.key = kb_key,
	.modifiers = kb_modifiers,
	.repeat_info = kb_repeat,
};

static void
seat_caps(void *data, struct wl_seat *s, uint32_t caps)
{
	(void)data;
	if ((caps & WL_SEAT_CAPABILITY_KEYBOARD) && !keyboard) {
		keyboard = wl_seat_get_keyboard(s);
		wl_keyboard_add_listener(keyboard, &kb_listener, NULL);
	}
}

static void
seat_name(void *data, struct wl_seat *s, const char *name)
{
	(void)data;
	(void)s;
	(void)name;
}

static const struct wl_seat_listener seat_listener = {
	.capabilities = seat_caps,
	.name = seat_name,
};

static void
reg_global(void *data, struct wl_registry *reg, uint32_t name,
           const char *iface, uint32_t ver)
{
	(void)data;
	if (strcmp(iface, wl_seat_interface.name) == 0) {
		uint32_t v = ver >= 2 ? 2 : 1;
		seat = wl_registry_bind(reg, name, &wl_seat_interface, v);
		wl_seat_add_listener(seat, &seat_listener, NULL);
	}
}

static void
reg_remove(void *data, struct wl_registry *reg, uint32_t name)
{
	(void)data;
	(void)reg;
	(void)name;
}

static const struct wl_registry_listener reg_listener = {
	.global = reg_global,
	.global_remove = reg_remove,
};

int
main(void)
{
	struct wl_display *display;
	struct wl_registry *reg;

	display = wl_display_connect(NULL);
	if (!display) {
		printf("{\"text\":\"??\",\"class\":\"unknown\",\"tooltip\":\"no wayland display\"}\n");
		fflush(stdout);
		return 1;
	}
	reg = wl_display_get_registry(display);
	wl_registry_add_listener(reg, &reg_listener, NULL);
	wl_display_roundtrip(display);
	wl_display_roundtrip(display);
	if (last_group == UINT32_MAX)
		emit(0);
	while (wl_display_dispatch(display) != -1) {
	}
	return 0;
}
