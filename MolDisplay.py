import molecule

header = """<svg version="1.1" width="1000" height="1000"
    xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""
offsetx = 500
offsety = 500

class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z

    def __str__(self):
        return '%s %d %d %d' % (self.atom.element, self.atom.x, self.atom.y, self.z)

    def svg(self):
        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (self.atom.x*100+offsetx, self.atom.y*100+offsety, radius[self.atom.element], element_name[self.atom.element])


class Bond:
    def __init__(self, c_bond):
        self.bond = c_bond
        self.z = c_bond.z

    def __str__(self):
        return '%d %d %d' % (self.bond.a1, self.bond.a2, self.bond.epairs)

    def svg(self):
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (
            offsetx + (self.bond.x1*100-self.bond.dy*10), offsety + (self.bond.y1*100+self.bond.dx*10), 
            offsetx + (self.bond.x1*100+self.bond.dy*10), offsety + (self.bond.y1*100-self.bond.dx*10),
            offsetx + (self.bond.x2*100+self.bond.dy*10), offsety + (self.bond.y2*100-self.bond.dx*10), 
            offsetx + (self.bond.x2*100-self.bond.dy*10), offsety + (self.bond.y2*100+self.bond.dx*10))


class Molecule(molecule.molecule):

    def __str__(self):
        for atom in self.atoms:
            print(atom)

        for bond in self.bonds:
            print(bond)
        

    def svg(self):
        result = header
        AtomsAndBonds = []


        for i in range(self.atom_no):
            AtomsAndBonds.append(Atom(self.get_atom(i)))
        
        for i in range(self.bond_no):
            AtomsAndBonds.append(Bond(self.get_bond(i)))


        for i in range(len(AtomsAndBonds)):
            for j in range(0, len(AtomsAndBonds) - i - 1):

                if AtomsAndBonds[j].z > AtomsAndBonds[j + 1].z:
                    temp = AtomsAndBonds[j]
                    AtomsAndBonds[j] = AtomsAndBonds[j+1]
                    AtomsAndBonds[j+1] = temp


        for c in AtomsAndBonds:
            result += c.svg()

        result = result + footer
        return result
    

    def parse(self, file):
        l = file.readline()
        l = file.readline()
        l = file.readline()
        # read fourth line of sdf file and decode it
        line = next(file) 
        # line = line.decode()
        line = line.split()

        atom_no = int(line[0]) 
        bond_no = int(line[1]) 

        # loop to read all the atoms and then append
        for i in range(atom_no):
            line = next(file)
            # line = line.decode()
            line = line.split()

            x = float(line[0])
            y = float(line[1])
            z = float(line[2])
            name = line[3]
            self.append_atom(name, x, y, z)

        # loop to read all the bonds and then append
        for i in range(bond_no):
            line = next(file)
            # line = line.decode()
            line = line.split()

            a1 = int(line[0])
            a2 = int(line[1])
            epairs = int(line[2])
            self.append_bond(a1-1, a2-1, epairs)

# main to test the svg output
if __name__ == '__main__':
    mol = Molecule()
    fp = open("water.sdf", "rb")
    mol.parse(fp)

    print(mol.svg())
    

    
