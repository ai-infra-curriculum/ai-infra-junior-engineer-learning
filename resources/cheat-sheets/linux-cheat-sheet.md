# Linux / Shell Cheat Sheet — AI Infrastructure Edition

Commands and patterns you will use daily on a Linux-based infra job.

## Files and Directories

```bash
ls -lah                          # long listing, all, human sizes
ls -lt                           # newest first
ls -lS                           # largest first

cd -                             # back to previous directory
pushd /tmp && popd               # bookmark + return

cp -r src/ dest/                 # recursive
cp -a src/ dest/                 # archive: preserves perms, timestamps, symlinks
mv old new
rm -rf bad/                      # careful

mkdir -p a/b/c                   # parents as needed
ln -sf /actual /link             # symlink (force-replace)

stat file                        # detailed metadata
file file                        # what kind is it
du -sh dir/                      # total size, human
df -h                            # disk free, human
```

## Finding Things

```bash
find . -name '*.log' -mtime -1                  # *.log modified in last 24h
find . -type f -size +100M                       # files >100 MB
find . -type f -exec grep -l "pattern" {} +      # grep across all
find . -type d -empty -delete                    # remove empty dirs

# Better alternatives if installed
fd 'pattern'                                     # faster find
rg 'pattern'                                     # faster grep
```

## grep + friends

```bash
grep -rn 'pattern' src/                          # recursive, line numbers
grep -rni 'pattern' --include='*.py' src/        # case-insensitive, glob
grep -rl 'pattern' src/                          # just filenames
grep -v 'noise'                                  # invert
grep -A 3 -B 1 'pattern'                         # 3 after, 1 before
grep -E 'foo|bar'                                # regex
```

## Pipes and Composition

```bash
# Top 5 largest files in a tree
du -h ./* 2>/dev/null | sort -h | tail -5

# Lines containing ERROR in the last 10 minutes of logs
journalctl --since "10 min ago" | grep -i error

# Count requests per status code in an nginx access log
awk '{print $9}' access.log | sort | uniq -c | sort -rn

# Top IPs hitting an endpoint
grep '/predict' access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head
```

## Permissions

```bash
chmod 755 script.sh              # rwxr-xr-x
chmod +x script.sh               # add execute
chmod -R u+rw,go-w dir/          # recursive symbolic
chown -R user:group dir/

# Read permissions
stat -c '%a %U %G %n' file
ls -l                            # human-readable

# What's blocking me?
namei -l /path/to/thing          # diagnose ACLs across the chain
```

## Processes

```bash
ps aux                           # all processes
ps -ef --forest                  # tree
pgrep -a -f 'pattern'            # by command
pkill -f 'pattern'               # kill by command
kill -9 <pid>                    # SIGKILL (last resort)
kill -15 <pid>                   # SIGTERM (let it clean up)

top                              # live
htop                             # nicer top, if installed
iotop                            # IO usage
iftop                            # network usage

# What's listening?
ss -tlnp                         # TCP listening + program
ss -tunp                         # all TCP/UDP + connections
lsof -i :8080                    # what's on port 8080
lsof -p <pid>                    # what files/sockets does this pid have open
```

## systemd

```bash
systemctl status nginx
systemctl start|stop|restart nginx
systemctl enable nginx           # start at boot
systemctl daemon-reload          # after editing a .service file

journalctl -u nginx -f           # follow logs
journalctl --since "1 hour ago" --until "10 min ago"
journalctl -u nginx --since today --no-pager | tail -200
```

## Networking

```bash
# Connectivity
ping -c 4 host
traceroute host
mtr host

# DNS
dig +short example.com
dig example.com @1.1.1.1         # query specific resolver
host -t MX example.com

# HTTP
curl -sS https://example.com
curl -v -X POST -H 'content-type: application/json' \
     -d '{"x":1}' https://example.com/api
curl -o file.tar.gz -L https://example.com/release.tar.gz
curl -I https://example.com      # headers only
curl -w '\n%{http_code} %{time_total}s\n' https://example.com

# Interface info
ip a
ip route
ip -s link show eth0             # statistics
```

## SSH

```bash
ssh user@host
ssh -i ~/.ssh/key.pem user@host
ssh -L 8080:remote-svc:80 user@host        # local port forward
ssh -R 8080:localhost:80 user@host         # remote port forward
ssh-keygen -t ed25519                       # generate key
ssh-copy-id user@host                       # install pubkey
~/.ssh/config:
    Host bastion
        HostName 10.0.0.1
        User you
        IdentityFile ~/.ssh/id_ed25519
```

## Text Manipulation

```bash
sed -i 's/old/new/g' file        # in-place replace
sed -n '20,40p' file             # print lines 20-40

awk '{print $1, $3}' file
awk -F',' '{print $2}' csv       # comma delimiter
awk '$3 > 100 {print}' file       # filter by column 3

cut -d',' -f1,3 csv               # columns 1 and 3
sort -k2 -n file                  # sort by column 2, numeric
sort -u                           # unique
uniq -c                           # count duplicates (after sort)

tr '[:upper:]' '[:lower:]'        # lowercase
tr -d '\r' < file                 # strip carriage returns

wc -l file                        # line count
head -n 20 file                   # first 20 lines
tail -f file                      # follow growth
tail -n 100 file
```

## tar / gzip

```bash
tar czf archive.tar.gz dir/      # create gzipped
tar xzf archive.tar.gz           # extract
tar tzf archive.tar.gz | head    # list
tar xzf archive.tar.gz -C /dst   # extract to specific path

gzip -9 file                     # compress (max ratio)
zcat file.gz | grep pattern      # search compressed
```

## Bash Scripting Basics

```bash
#!/usr/bin/env bash
set -euo pipefail        # exit on error, unset vars, pipe failures
IFS=$'\n\t'              # safer field splitting

# Variables
name="value"
readonly CONFIG="/etc/app.conf"
PATH="/usr/local/bin:$PATH"

# Args
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <arg>" >&2
    exit 1
fi
input="$1"
shift

# Conditionals
if [[ -f /etc/passwd ]]; then ...; fi
if [[ "$x" == "go" ]]; then ...; fi

# Loops
for f in *.log; do
    echo "$f"
done

while IFS= read -r line; do
    echo "$line"
done < file.txt

# Functions
greet() {
    local name="$1"
    echo "hi $name"
}
greet world

# Trap for cleanup
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
```

## Job Control

```bash
sleep 100 &              # background
jobs                     # list
fg %1                    # foreground
bg %1                    # background-resume
Ctrl-Z                   # suspend
nohup long_cmd &         # survive logout
disown                   # detach from shell
```

## Disk and Filesystems

```bash
df -h                    # filesystem use
du -sh dir/              # one dir total
du -h --max-depth=1 .    # one level deep
ncdu                     # interactive disk usage (if installed)

lsblk                    # block devices
mount | column -t        # mounted filesystems
```

## Useful Shortcuts

| Key | Effect |
|---|---|
| `Ctrl-R` | Reverse-incremental history search |
| `Ctrl-A` / `Ctrl-E` | Beginning / end of line |
| `Ctrl-W` | Delete previous word |
| `Ctrl-U` | Delete to start of line |
| `Ctrl-L` | Clear screen |
| `Alt-.` | Last argument of previous command |
| `!!` | Previous command |
| `!$` | Last argument of previous command |
| `^old^new` | Re-run previous with substitution |

## Common Gotchas

- **`rm -rf $VAR/`** — if `VAR` is empty, this becomes `rm -rf /`. Always quote and check.
- **Filenames with spaces** — quote everything: `"$f"`, not `$f`.
- **`cat foo | grep bar`** — useless cat. Just `grep bar foo`.
- **`for f in $(ls)`** — breaks on spaces. Use `for f in *` or `find ... -print0 | xargs -0`.
- **No `set -e`** in scripts — errors get silently ignored. Always `set -euo pipefail`.
- **Bash version** — macOS ships ancient bash 3.2. Use `#!/usr/bin/env bash` and test on Linux.

## See Also

- `man bash`, `man bash-builtins`
- [ShellCheck](https://www.shellcheck.net/) — lint your scripts
- [explainshell.com](https://explainshell.com/) — annotated command breakdowns
