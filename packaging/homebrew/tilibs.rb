# SPDX-License-Identifier: GPL-3.0-or-later
# Candidate for a custom tap; pinned upstream snapshot, not a core submission.
class Tilibs < Formula
  desc "Link and file libraries for Texas Instruments calculators"
  homepage "https://github.com/debrouxl/tilibs"
  url "https://codeload.github.com/debrouxl/tilibs/tar.gz/6dba390e7390c4b98ae96287b39a3971c331fbef"
  version "2026.10.11"
  sha256 "c6c37882b73e86d6bee6f9b253976479491ab4956fbf5e556e3a585c66c94a50"
  license "GPL-2.0-or-later"

  depends_on "cmake" => :build
  depends_on "pkgconf" => :build
  depends_on "glib"
  depends_on "libarchive"
  depends_on "libusb"

  def install
    system "cmake", "-S", ".", "-B", "build", "-DBUILD_TESTS=OFF", *std_cmake_args
    system "cmake", "--build", "build"
    system "cmake", "--install", "build"
    %w[libticonv libtifiles libticables libticalcs].each do |component|
      (share/"licenses"/"tilibs"/component).install "#{component}/trunk/COPYING"
    end
  end
end
