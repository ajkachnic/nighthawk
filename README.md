# nighthawk

smol compiler, using Python, QBE (compiler backend), and Lark (parser generator)

## why

idk, i was bored and then i made this...

## but how do i run it??

```sh
nix-shell # use nix like a chad

python src/main.py < tests/expressions.lark > out.ssa # Outputs QBE IR
qbe out.ssa > out.s # Turn QBE IR into assembly
gcc out.s -o out # Turn assembly into binary

./out # woah magic
```

### but what if i don't want to use nix?

install nix and refer to **but how do i run it??**.

#### but seriously, how do i do run it without nix???

don't.

##### okay but actually...

- Install Python 3.10 (or later)
- Install QBE (or compile from scratch)

```sh
pip install lark

# Run the commands from the other thing, minus the `nix-shell`
```
