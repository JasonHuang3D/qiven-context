# Toolchain Win

Genesis historical import status: **SLICE COMPLETE** for the current pinned executable-tool boundary.

## Current verified state

Pinned live main during Genesis:

`a79825031e838d80354d31489c87327dd6adbfb7`

`toolchain.json` currently declares:

- clang-format `19.1.7` at `bin/clang-format.exe`, sourced from `llvm-project/llvmorg-19.1.7`;
- CMake `4.4.3` at `cmake/bin/cmake.exe`, sourced from `Kitware/CMake/v4.4.3`.

## Responsibility boundary

qiven-toolchain-win owns pinned executable build tools that Qiven repositories can resolve deterministically on Windows.

It does not own repository conventions, engineering protocol, templates, adoption/synchronization policy, or domain architecture. Those responsibilities belong to qiven-devkit and the runtime/domain repositories as captured by ADR-0010.

The current manifest should not be read as proof that MSVC, the Windows SDK, CUDA, Python, or every host dependency is pinned by this repository. Add or change pins only when a concrete shared-tool requirement justifies doing so.

## Evidence

See `MEM-20260913T185050Z-18E61C` and `evidence/audits/genesis-cross-domain-residue.md`.
