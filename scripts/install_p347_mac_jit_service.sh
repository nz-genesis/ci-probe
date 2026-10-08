#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNNER_SCRIPT="$SCRIPT_DIR/p347_mac_jit_runner.sh"
PLIST_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$PLIST_DIR/com.nz-genesis.p347-mac-runner.plist"
LOG_DIR="$HOME/Library/Logs"
LABEL="com.nz-genesis.p347-mac-runner"

test -x "$RUNNER_SCRIPT" || chmod 700 "$RUNNER_SCRIPT"
mkdir -p "$PLIST_DIR" "$LOG_DIR"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER_SCRIPT</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ProcessType</key>
  <string>Background</string>
  <key>StandardOutPath</key>
  <string>$LOG_DIR/p347-mac-runner.log</string>
  <key>StandardErrorPath</key>
  <string>$LOG_DIR/p347-mac-runner.error.log</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "P347 Mac JIT runner LaunchAgent installed."
echo "Status:"
launchctl print "gui/$(id -u)/$LABEL" | sed -n '1,35p'
echo
echo "Logs: $LOG_DIR/p347-mac-runner.log"
echo "Errors: $LOG_DIR/p347-mac-runner.error.log"
