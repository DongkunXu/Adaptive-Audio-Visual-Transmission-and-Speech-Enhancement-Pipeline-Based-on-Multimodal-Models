TEMPLATE = app

win32:CONFIG += console
CONFIG -= qt

SOURCES += \
    cpp-example.cpp \
    device.cpp \
    calibration-example.cpp \
    enumerating-example.cpp \
    scan-example.cpp \
    using_plain_api_binding_example.cpp

INCLUDEPATH += "$$PWD/../"

FORCEDARCH=$$(FORCEDARCH)
contains(QT_ARCH, i386):!contains(FORCEDARCH, x64) {
    ARCH=x32
} else {
    ARCH=x64
}

linux {
   contains(ARCH, x32):LIBS += "$$PWD/../libPocketVnaApi_x32.so"
   else:contains(ARCH, x64):LIBS += "$$PWD/../libPocketVnaApi_x64.so"
}

win32 {
   *-g++*|clang|gcc {
       LIBS += "$$PWD/../PocketVnaApi_x32.dll"
   }
}

macos {
   LIBS += "$$PWD/../libPocketVnaApi_x64.dylib"
}

#-mthreads
#-pthread -- support for multithreading
#-lpthread -- link against libpthread
# easiest way to add support into qmake is using CONFIG += thread

CONFIG += c++11 \
        warn_on \
        thread     #-lpthread

DESTDIR += "$$_PRO_FILE_PWD_"

HEADERS += \
    progress-listener.h \
    literals.h \
    device-enumerator.h \
    device-handler.h \
    device-properties.h \
    device.h \
    predefines.h \
    calibration-wrapper.h \
    scope-guard.h
