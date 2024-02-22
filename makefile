CC = clang
CFLAGS = -Wall -std=c99 -pedantic
INC = /usr/include/python3.7m
LIB = /usr/lib/python3.7/config-3.7m-x86_64-linux-gnu
PYTHON_VERSION = 3.7m

all: _molecule.so

clean:  
	rm -f *.o *.so mol

libmol.so: mol.o
	$(CC) -shared mol.o -o libmol.so -lm

mol.o:  mol.c mol.h
	$(CC) $(CFLAGS) -c -fPIC mol.c -o mol.o

main.o:  main.c mol.h
	$(CC) $(FLAGS) -c main.c -o main.o

molecule_wrap.o: swig molecule_wrap.c
	$(CC) $(CFLAGS) -c -fPIC -I $(INC) molecule_wrap.c -o molecule_wrap.o

swig: molecule.i
	swig -python molecule.i

_molecule.so: libmol.so molecule_wrap.o
	$(CC) $(CFLAGS) -shared -L. -lmol -L $(LIB) -lpython$(PYTHON_VERSION) -dynamiclib -o _molecule.so molecule_wrap.o
