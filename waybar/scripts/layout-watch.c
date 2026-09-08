/* Mirror dwl xkb (us,ru colemak + grp:ctrl_shift_toggle) from evdev.
 * Display-only: writes $XDG_RUNTIME_DIR/dwl-layout. Does not inject keys. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <xkbcommon/xkbcommon.h>

static const char *label(xkb_layout_index_t idx)
{
	switch (idx) {
	case 0:
		return "en";
	case 1:
		return "ru";
	default:
		return "??";
	}
}

static void
write_layout(const char *l)
{
	const char *rt = getenv("XDG_RUNTIME_DIR");
	char path[256], tmp[280];
	FILE *f;

	if (!rt)
		return;
	if (snprintf(path, sizeof(path), "%s/dwl-layout", rt) >= (int)sizeof(path))
		return;
	if (snprintf(tmp, sizeof(tmp), "%s.tmp", path) >= (int)sizeof(tmp))
		return;
	f = fopen(tmp, "w");
	if (!f)
		return;
	fputs(l, f);
	fputc('\n', f);
	fclose(f);
	rename(tmp, path);
}

static void
log_line(FILE *log, const char *msg)
{
	struct timespec ts;
	clock_gettime(CLOCK_REALTIME, &ts);
	fprintf(log, "%ld.%03ld %s\n", (long)ts.tv_sec, ts.tv_nsec / 1000000, msg);
	fflush(log);
}

int
main(int argc, char **argv)
{
	const char *dev = getenv("KEYBOARD_EVENT");
	if (!dev || !dev[0])
		dev = "/dev/input/event4";
	const char *logpath = "/tmp/layout-watch.log";
	int fd;
	FILE *log;
	struct xkb_context *ctx;
	struct xkb_keymap *keymap;
	struct xkb_state *state;
	struct xkb_rule_names names = {
		.layout = "us,ru",
		.variant = "colemak, ",
		.options = "grp:ctrl_shift_toggle",
	};
	xkb_layout_index_t last = 0;
	struct input_event ev;
	char buf[128];

	if (argc >= 2)
		dev = argv[1];

	fd = open(dev, O_RDONLY);
	if (fd < 0) {
		fprintf(stderr, "layout-watch: open %s: %s\n", dev, strerror(errno));
		return 1;
	}

	log = fopen(logpath, "a");
	if (!log)
		log = stderr;

	ctx = xkb_context_new(XKB_CONTEXT_NO_FLAGS);
	keymap = xkb_keymap_new_from_names(ctx, &names, XKB_KEYMAP_COMPILE_NO_FLAGS);
	if (!keymap) {
		fprintf(stderr, "layout-watch: keymap compile failed\n");
		return 1;
	}
	state = xkb_state_new(keymap);
	write_layout(label(last));
	snprintf(buf, sizeof(buf), "start device=%s group=%s", dev, label(last));
	log_line(log, buf);

	while (read(fd, &ev, sizeof(ev)) == (ssize_t)sizeof(ev)) {
		xkb_layout_index_t now;
		enum xkb_key_direction dir;

		if (ev.type != EV_KEY)
			continue;
		if (ev.value != 0 && ev.value != 1)
			continue; /* ignore autorepeat */
		dir = ev.value ? XKB_KEY_DOWN : XKB_KEY_UP;
		xkb_state_update_key(state, (xkb_keycode_t)(ev.code + 8), dir);
		now = xkb_state_serialize_layout(state, XKB_STATE_LAYOUT_EFFECTIVE);
		if (now != last) {
			last = now;
			write_layout(label(now));
			snprintf(buf, sizeof(buf), "group=%s key=%u %s",
			         label(now), ev.code, ev.value ? "down" : "up");
			log_line(log, buf);
		}
	}
	log_line(log, "exit");
	return 0;
}
