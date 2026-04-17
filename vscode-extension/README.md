# Plain Language — VSCode Extension

Syntax highlighting for `.plain` files.

## What it highlights

- **Keywords** — `set`, `to`, `if`, `then`, `else`, `end`, `fn`, `return`, `repeat`, `while`, `and`, `or`, `not`, `import`, `times`, `with`, `in`, `add`, `at`
- **Built-in functions** — `say`, `ask`, `num`, `str`, `len`, `random`
- **Function names** — the identifier immediately after `fn`
- **Strings** — anything in double quotes
- **Numbers** — integers and floats
- **Comments** — lines (or inline) starting with `#`

## Installation (local)

Copy this folder into your VS Code extensions directory:

```bash
cp -r vscode-extension ~/.vscode/extensions/plain-lang
```

Then restart VS Code (or run **Developer: Reload Window** from the command palette).

Any file ending in `.plain` will now be highlighted automatically.

## Uninstall

```bash
rm -rf ~/.vscode/extensions/plain-lang
```
