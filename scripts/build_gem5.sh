#!/bin/bash
# Compila gem5 (v26, sistema Kconfig) para ARM en dos variantes:
#   build/ARM_MESI  -> Ruby MESI_Two_Level
#   build/ARM_MOESI -> Ruby MOESI_CMP_directory
# Ambas sirven también con caches clásicas (E1-E4).
# Uso: bash build_gem5.sh [jobs]   (por defecto 4, seguro con ~7 GB de RAM)
set -e
JOBS=${1:-4}
cd ~/gem5

mkdir -p ~/gem5-opts
cat > ~/gem5-opts/ARM_MESI <<'EOF'
BUILD_ISA=y
USE_ARM_ISA=y
RUBY=y
PROTOCOL="MESI_Two_Level"
RUBY_PROTOCOL_MESI_Two_Level=y
EOF
cat > ~/gem5-opts/ARM_MOESI <<'EOF'
BUILD_ISA=y
USE_ARM_ISA=y
RUBY=y
PROTOCOL="MOESI_CMP_directory"
RUBY_PROTOCOL_MOESI_CMP_directory=y
EOF

for V in ARM_MESI ARM_MOESI; do
  echo "=== $(date) · configurando $V"
  [ -f build/$V/gem5.config ] || scons defconfig build/$V ~/gem5-opts/$V
  echo "=== $(date) · compilando $V con -j$JOBS"
  scons build/$V/gem5.opt -j"$JOBS" </dev/null
  echo "=== $(date) · $V listo"
done
echo "=== TODO LISTO"
