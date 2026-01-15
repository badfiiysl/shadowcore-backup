#!/bin/bash
echo "🔍 Tracing actual service files from running processes..."
echo "=========================================================="

# Function to trace a process
trace_process() {
    local pid=$1
    local cmd=$2
    echo "=== PID $pid: $cmd ==="
    
    # Get exe location
    if [ -f "/proc/$pid/exe" ]; then
        exe=$(readlink -f "/proc/$pid/exe")
        echo "   Executable: $exe"
    fi
    
    # Get cwd
    if [ -f "/proc/$pid/cwd" ]; then
        cwd=$(readlink -f "/proc/$pid/cwd")
        echo "   Working dir: $cwd"
    fi
    
    # Get command line
    if [ -f "/proc/$pid/cmdline" ]; then
        cmdline=$(tr '\0' ' ' < "/proc/$pid/cmdline")
        echo "   Full command: $cmdline"
    fi
    
    # Get open files
    echo "   Open files:"
    lsof -p $pid 2>/dev/null | grep -E "\.(py|js)$" | head -5 | awk '{print "     " $9}'
    echo ""
}

# Get all shadowcore PIDs
echo "Python processes:"
ps aux | grep "[p]ython" | grep -i shadow | while read line; do
    pid=$(echo $line | awk '{print $2}')
    cmd=$(echo $line | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}')
    trace_process "$pid" "$cmd"
done

echo "Node.js processes:"
ps aux | grep "[n]ode" | grep -i shadow | while read line; do
    pid=$(echo $line | awk '{print $2}')
    cmd=$(echo $line | awk '{for(i=11;i<=NF;i++) printf $i" "; print ""}')
    trace_process "$pid" "$cmd"
done

echo "📁 Checking if /opt paths are symlinks:"
for path in /opt/shadowcore* /opt/shadowbrain /opt/shadowsearch /opt/threat-insight; do
    if [ -e "$path" ]; then
        if [ -L "$path" ]; then
            target=$(readlink -f "$path")
            echo "🔗 $path -> $target"
        else
            echo "📂 $path (directory)"
            # List first few files
            find "$path" -name "*.py" -o -name "*.js" 2>/dev/null | head -3
        fi
    fi
done
