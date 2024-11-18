{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  nativeBuildInputs = with pkgs.buildPackages; [
    ffmpeg
    python3
    python311Packages.pygame
    python311Packages.requests
  ];
}
