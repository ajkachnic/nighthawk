with (import <nixpkgs> {});
mkShell {
  buildInputs = [
    qbe
    tinycc

    (python310.withPackages (ps: [ ps.lark ]))
  ];
}
