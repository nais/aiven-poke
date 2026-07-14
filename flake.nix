{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import inputs.nixpkgs { localSystem = { inherit system; }; };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python3
            pkgs.uv
            pkgs.ruff
            pkgs.basedpyright
          ];
        };
      }
    );
}
