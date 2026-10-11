# SPDX-License-Identifier: GPL-3.0-or-later
cmake_minimum_required(VERSION 3.16)
project(tilem_portable VERSION 2.0.2 LANGUAGES C)
include(GNUInstallDirs)
include(CTest)
include(CheckLibraryExists)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
option(TILEM_BUILD_GTK "Build the original GTK 2 emulator and debugger" ON)
configure_file(cmake/config.h.in config.h)
set(CORE_SOURCES
  emu/calcs.c
  emu/cert.c
  emu/flash.c
  emu/graycolor.c
  emu/grayimage.c
  emu/graylcd.c
  emu/keypad.c
  emu/lcd.c
  emu/link.c
  emu/md5.c
  emu/monolcd.c
  emu/rom.c
  emu/state.c
  emu/timers.c
  emu/x1/x1_init.c
  emu/x1/x1_io.c
  emu/x1/x1_memory.c
  emu/x1/x1_subcore.c
  emu/x2/x2_init.c
  emu/x2/x2_io.c
  emu/x2/x2_memory.c
  emu/x2/x2_subcore.c
  emu/x3/x3_init.c
  emu/x3/x3_io.c
  emu/x3/x3_memory.c
  emu/x3/x3_subcore.c
  emu/x4/x4_init.c
  emu/x4/x4_io.c
  emu/x4/x4_memory.c
  emu/x4/x4_subcore.c
  emu/x5/x5_init.c
  emu/x5/x5_io.c
  emu/x5/x5_memory.c
  emu/x5/x5_subcore.c
  emu/x6/x6_init.c
  emu/x6/x6_io.c
  emu/x6/x6_memory.c
  emu/x6/x6_subcore.c
  emu/x7/x7_init.c
  emu/x7/x7_io.c
  emu/x7/x7_memory.c
  emu/x7/x7_subcore.c
  emu/xn/xn_init.c
  emu/xn/xn_io.c
  emu/xn/xn_memory.c
  emu/xn/xn_subcore.c
  emu/xp/xp_init.c
  emu/xp/xp_io.c
  emu/xp/xp_memory.c
  emu/xp/xp_subcore.c
  emu/xs/xs_init.c
  emu/xs/xs_io.c
  emu/xs/xs_memory.c
  emu/xs/xs_subcore.c
  emu/xz/xz_init.c
  emu/xz/xz_io.c
  emu/xz/xz_memory.c
  emu/xz/xz_subcore.c
  emu/z80.c
)
add_library(tilemcore STATIC ${CORE_SOURCES})
set_target_properties(tilemcore PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_compile_definitions(tilemcore PRIVATE HAVE_CONFIG_H)
target_include_directories(tilemcore PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/emu PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
check_library_exists(m pow "" TILEM_HAVE_LIBM)
if(TILEM_HAVE_LIBM)
  target_link_libraries(tilemcore PUBLIC m)
endif()
add_library(tilembridge SHARED server/bridge.c cli/runtime.c)
target_link_libraries(tilembridge PRIVATE tilemcore)
set_target_properties(tilembridge PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION 1)
add_executable(tilem-headless cli/main.c cli/runtime.c)
target_link_libraries(tilem-headless PRIVATE tilemcore)
if(BUILD_TESTING)
  add_executable(tilem-core-test tests/core.c cli/runtime.c)
  target_link_libraries(tilem-core-test PRIVATE tilemcore)
  add_test(NAME core COMMAND tilem-core-test)
  add_test(NAME headless-help COMMAND tilem-headless --help)
endif()
install(TARGETS tilembridge tilem-headless
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(PROGRAMS server/tilem-server DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES server/index.html server/server.py DESTINATION ${CMAKE_INSTALL_DATADIR}/tilem-portable/server)
install(FILES COPYING COPYING.LESSER docs/LICENSING.md DESTINATION ${CMAKE_INSTALL_DATADIR}/licenses/tilem-portable)
if(TILEM_BUILD_GTK)
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(GTK REQUIRED IMPORTED_TARGET gtk+-2.0>=2.6 glib-2.0>=2.32 gthread-2.0)
  pkg_check_modules(TICALCS REQUIRED IMPORTED_TARGET ticalcs2 ticables2 tifiles2 ticonv)
  # Keep each macOS -framework pair together through CMake's option deduplication.
  # FindPkgConfig can leave these in LINK_OPTIONS when reusing its cache.
  if(APPLE)
    foreach(dependency GTK TICALCS)
      get_target_property(options PkgConfig::${dependency} INTERFACE_LINK_OPTIONS)
      if(options)
        set(grouped)
        set(expect_framework FALSE)
        foreach(option IN LISTS options)
          if(expect_framework)
            list(APPEND grouped "SHELL:-framework ${option}")
            set(expect_framework FALSE)
          elseif(option STREQUAL "-framework")
            set(expect_framework TRUE)
          else()
            list(APPEND grouped "${option}")
          endif()
        endforeach()
        set_property(TARGET PkgConfig::${dependency} PROPERTY INTERFACE_LINK_OPTIONS "${grouped}")
      endif()
    endforeach()
  endif()
  add_library(tilemdb STATIC db/disasm.c db/listing.c db/lstfile.c)
  target_link_libraries(tilemdb PUBLIC tilemcore)
  target_include_directories(tilemdb PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/db PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
  target_compile_definitions(tilemdb PRIVATE HAVE_CONFIG_H)
  add_executable(tilem2
    gui/address.c
    gui/animatedgif.c
    gui/animation.c
    gui/breakpoints.c
    gui/charmap.c
    gui/config.c
    gui/control.c
    gui/debugger.c
    gui/disasmview.c
    gui/emucore.c
    gui/emulator.c
    gui/emuwin.c
    gui/event.c
    gui/filedlg.c
    gui/files.c
    gui/fixedtreeview.c
    gui/gifencod.c
    gui/icons.c
    gui/keybindings.c
    gui/keypaddlg.c
    gui/link.c
    gui/macos.c
    gui/macro.c
    gui/memmodel.c
    gui/memory.c
    gui/memview.c
    gui/menu.c
    gui/pbar.c
    gui/preferences.c
    gui/rcvmenu.c
    gui/screenshot.c
    gui/sendfile.c
    gui/skinops.c
    gui/ti81prg.c
    gui/tilem2.c
    gui/tool.c
  )
  target_include_directories(tilem2 PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
  target_compile_definitions(tilem2 PRIVATE HAVE_CONFIG_H
    SHARE_DIR="${CMAKE_INSTALL_FULL_DATADIR}/tilem2"
    UNINSTALLED_SHARE_DIR="${CMAKE_CURRENT_SOURCE_DIR}/data")
  target_link_libraries(tilem2 PRIVATE tilemdb tilemcore PkgConfig::GTK PkgConfig::TICALCS)
  if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    # With CMAKE_C_EXTENSIONS OFF, glibc hides S_ISSOCK (gui/control.c) unless a
    # feature-test macro is set. Linux only: other platforms build as before.
    target_compile_definitions(tilem2 PRIVATE _DEFAULT_SOURCE)
  endif()
  install(TARGETS tilem2 RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
  install(DIRECTORY data/skins data/symbols DESTINATION ${CMAKE_INSTALL_DATADIR}/tilem2)
  install(FILES data/keybindings.ini DESTINATION ${CMAKE_INSTALL_DATADIR}/tilem2)
  install(DIRECTORY data/icons/hicolor DESTINATION ${CMAKE_INSTALL_DATADIR}/icons)
  install(FILES data/desktop/tilem2.desktop DESTINATION ${CMAKE_INSTALL_DATADIR}/applications)
  install(FILES data/desktop/tilem2.xml DESTINATION ${CMAKE_INSTALL_DATADIR}/mime/packages)
endif()
set(CPACK_PACKAGE_NAME tilem-portable)
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_SOURCE_GENERATOR "TGZ")
set(CPACK_SOURCE_IGNORE_FILES "/\\.git/;/\\.deps/;/build[^/]*/;/_install/;/var/;/[^/]*\\.app/;__pycache__;\\.rom$;\\.ROM$;\\.sav$")
include(CPack)
