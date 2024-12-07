# makefile for Stellar
#
# Type "make" or "make mac" to compile Stellar on a Mac system.
# Type "make linux" to compile Stellar on a Linux-like system.
# Type "make showme" to compile Show Me on a system with X Windows.
#
# Type "make clean" to delete all executable and object files.

# location of the Stellar source files
SRC = ./src/
# location of the produced executables
BIN = ./

# CC should be set to the name of your favorite C compiler.
CC = clang

# RM should be set to the name of your favorite rm (file deletion program).
RM = /bin/rm

# Switches for C compiler
CSWITCHES = -g -DSELF_CHECK -Wall -Wconversion -Wstrict-prototypes \
    -Wno-strict-aliasing -fno-strict-aliasing -I$(SRC)

CSWITCHESFAST = -DSELF_CHECK -O3 -Wall -Wconversion -Wstrict-prototypes \
    -Wno-strict-aliasing -fno-strict-aliasing -I$(SRC)

# Mac-specific switches (removed PPC architecture, updated for modern macOS)
CSWITCHESMAC = -arch arm64 -arch x86_64 -g -DSELF_CHECK -Wall \
    -Wno-strict-aliasing -fno-strict-aliasing -Wconversion -Wstrict-prototypes \
    -I$(SRC) -I/opt/X11/include -L/opt/X11/lib

CSWITCHESSTELLARMAC = -pedantic -g -DSELF_CHECK -Wall -Wno-strict-aliasing \
    -fno-strict-aliasing -Wconversion -Wstrict-prototypes -I$(SRC)

CSWITCHESSTELLARMACFAST = -arch arm64 -arch x86_64 -pedantic -O3 -Wall \
    -Wno-strict-aliasing -fno-strict-aliasing -Wconversion -Wstrict-prototypes -I$(SRC)

# Updated X11 paths for modern macOS
SHOWMESWITCHES = -I/opt/X11/include -L/opt/X11/lib

STARLIBDEFS = -DNOMAIN

# sources for Stellar
STELLARSRCS = $(SRC)Stellar.c $(SRC)arraypoolstack.c $(SRC)classify.c \
    $(SRC)insertion.c $(SRC)interact.c $(SRC)journal.c $(SRC)main.c \
    $(SRC)output.c $(SRC)print.c $(SRC)quadric.c $(SRC)anisotropy.c \
    $(SRC)quality.c $(SRC)size.c $(SRC)smoothing.c $(SRC)top.c \
    $(SRC)topological.c $(SRC)vector.c $(SRC)improve.c $(SRC)Starbase.c

all: mac
mac: $(BIN)Stellarmac
macdebug: $(BIN)Stellarmacdebug
macshowme: $(BIN)showmemac
linux: $(BIN)Stellarlinux
linuxdebug: $(BIN)Stellarlinuxdebug
linuxshowme: $(BIN)showmelinux

$(BIN)Stellarlinux: $(BIN)Starbase.o $(STELLARSRCS)
	$(CC) $(CSWITCHESFAST) -o $(BIN)Stellar $(SRC)Stellar.c \
		$(BIN)Starbase.o -lm

$(BIN)Stellarlinuxdebug: $(BIN)Starbase.o $(STELLARSRCS)
	$(CC) $(CSWITCHES) -o $(BIN)Stellardebug $(SRC)Stellar.c \
		$(BIN)Starbase.o -lm

$(BIN)Stellarmac: $(BIN)Starbasemac.o $(STELLARSRCS)
	$(CC) $(CSWITCHESSTELLARMACFAST) -o $(BIN)Stellar $(SRC)Stellar.c \
		$(BIN)Starbasemac.o -lm

$(BIN)Stellarmacdebug: $(BIN)Starbasemac.o $(STELLARSRCS)
	$(CC) $(CSWITCHESSTELLARMAC) -o $(BIN)Stellardebug $(SRC)Stellar.c \
		$(BIN)Starbasemac.o -lm

$(BIN)Starbasemac.o: $(SRC)Starbase.c $(SRC)Starbase.h
	$(CC) $(CSWITCHESMAC) $(STARLIBDEFS) -c -o $(BIN)Starbasemac.o \
		$(SRC)Starbase.c

$(BIN)Starbase.o: $(SRC)Starbase.c $(SRC)Starbase.h
	$(CC) $(CSWITCHESFAST) $(STARLIBDEFS) -c -o $(BIN)Starbase.o \
		$(SRC)Starbase.c

$(BIN)showmelinux: $(SRC)showme.c
	$(CC) $(CSWITCHESFAST) $(SHOWMESWITCHES) -o $(BIN)showme \
		$(SRC)showme.c -lX11 -lm

$(BIN)showmemac: $(SRC)showme.c
	$(CC) $(CSWITCHESMAC) $(SHOWMESWITCHES) -o $(BIN)showme \
		$(SRC)showme.c -lX11 -lm

clean:
	-$(RM) $(BIN)Starbase.o $(BIN)Starbasemac.o $(BIN)Stellar $(BIN)Stellardebug $(BIN)showme
