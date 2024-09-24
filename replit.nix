{pkgs}: {
  deps = [
    pkgs.libGL
    pkgs.postgresql
    pkgs.python3
    pkgs.python310Packages.pip
    pkgs.imagemagick
  ];
}
