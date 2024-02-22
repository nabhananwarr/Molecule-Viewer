import os;
import sqlite3;
import MolDisplay;
import molecule;

class Database():
    
    def __init__(self, reset=False):
        if reset == True:
            if os.path.exists( 'molecules.db' ):
                os.remove( 'molecules.db' );

        # create database file if it doesn't exist and connect to it
        self.conn = sqlite3.connect( 'molecules.db' );
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements
                        ( ELEMENT_NO     INTEGER NOT NULL,
                        ELEMENT_CODE     VARCHAR(3) PRIMARY KEY,
                        ELEMENT_NAME     VARCHAR(32) NOT NULL,
                        COLOUR1          CHAR(6) NOT NULL,
                        COLOUR2          CHAR(6) NOT NULL,
                        COLOUR3        	 CHAR(6) NOT NULL,
                        RADIUS           DECIMAL(3) NOT NULL );""" );

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms
                        ( ATOM_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
                        ELEMENT_CODE     VARCHAR(3) NOT NULL,
                        X                DECIMAL(7,4) NOT NULL,
                        Y                DECIMAL(7,4) NOT NULL,
                        Z                DECIMAL(7,4) NOT NULL,
                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE));""" );

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds
                        ( BOND_ID        INTEGER PRIMARY KEY AUTOINCREMENT,
                        A1               INTEGER NOT NULL,
                        A2               INTEGER NOT NULL,
                        EPAIRS           INTEGER NOT NULL );""" );

        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules
                        ( MOLECULE_ID    INTEGER PRIMARY KEY,
                        NAME             TEXT NOT NULL );""" );

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom
                        ( MOLECULE_ID     INTEGER NOT NULL AUTOINCREMENT,
                        Atom_ID           INTEGER NOT NULL,
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                        FOREIGN KEY (ATOM_ID) REFERENCES Atoms,
                        PRIMARY KEY (MOLECULE_ID, ATOM_ID) );""" );

        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond
                        ( MOLECULE_ID     INTEGER NOT NULL,
                        BOND_ID	          INTEGER NOT NULL,
                        FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules,
                        FOREIGN KEY (BOND_ID) REFERENCES Bonds,
                        PRIMARY KEY (MOLECULE_ID, BOND_ID) );""" );
        
        self.conn.commit()

    def __setitem__( self, table, values ):

        if(table == 'Elements'):
            self.conn.execute( """ INSERT
                                INTO Elements
                                VALUES (?, ?, ?, ?, ?, ?, ?);""", values )
            
        if(table == 'Atoms'):
            self.conn.execute( """ INSERT
                            INTO Atoms
                            VALUES (?, ?, ?, ?, ?);""", values )
            
        if(table == 'Bonds'):
            self.conn.execute( """ INSERT
                            INTO Bonds
                            VALUES (?, ?, ?, ?);""", values )
            
        if(table == 'Molecules'):
            self.conn.execute( """ INSERT
                            INTO Molecules
                            VALUES (?, ?);""", values )
            
        if(table == 'MoleculeAtom'):
            self.conn.execute( """ INSERT
                            INTO MoleculeAtom
                            VALUES (?, ?);""", values )
            
        if(table == 'MoleculeBond'):
            self.conn.execute( """ INSERT
                            INTO MoleculeBond
                            VALUES (?, ?);""", values )
            
        self.conn.commit()

    def add_atom( self, molname, atom ):

        self.conn.execute( """ INSERT
                            INTO Atoms (ELEMENT_CODE, X, Y, Z)
                            VALUES ('""" + atom.atom.element + """', '""" + str(atom.atom.x) + """', '""" + str(atom.atom.y) + """', '""" + str(atom.atom.z) + """' );""" )
        
        self.cursor.execute("SELECT ATOM_ID FROM Atoms ORDER BY ATOM_ID DESC LIMIT 1")
        atomIDresult = self.cursor.fetchone()
        self.cursor.execute(f"SELECT MOLECULE_ID FROM Molecules WHERE NAME='{molname}'")
        moleculeIDresult = self.cursor.fetchone()

        # print( atomIDresult, moleculeIDresult )
        self.conn.execute( f""" INSERT
                            INTO MoleculeAtom (MOLECULE_ID, ATOM_ID)
                            VALUES (" {moleculeIDresult[0]} ", " {atomIDresult[0]} ");""")
        self.conn.commit()


    def add_bond( self, molname, bond ):

        self.conn.execute( """ INSERT
                            INTO Bonds (A1, A2, epairs)
                            VALUES ('""" + str(bond.bond.a1) + """', '""" + str(bond.bond.a2) + """', '""" + str(bond.bond.epairs) + """' );""" )
        
        self.cursor.execute("SELECT BOND_ID FROM Bonds ORDER BY BOND_ID DESC LIMIT 1")
        bondIDresult = self.cursor.fetchone()
        self.cursor.execute(f"SELECT MOLECULE_ID FROM Molecules WHERE NAME='{molname}'")
        moleculeIDresult = self.cursor.fetchone()

        self.conn.execute( f""" INSERT
                            INTO MoleculeBond (MOLECULE_ID, BOND_ID)
                            VALUES (" {moleculeIDresult[0]} ", " {bondIDresult[0]} ");""")
        self.conn.commit()


    def add_molecule( self, name, fp ):

        mol = MolDisplay.Molecule()
        mol.parse(fp)

        self.conn.execute( f""" INSERT INTO Molecules (NAME) 
                                VALUES ('{name}');""")

        self.conn.commit()
        for i in range(mol.atom_no):
            self.add_atom(name, MolDisplay.Atom(mol.get_atom(i)))
        
        for i in range(mol.bond_no):
            self.add_bond(name, MolDisplay.Bond(mol.get_bond(i)))

        self.conn.commit()
    

    def load_mol( self, name ):

        mol = MolDisplay.Molecule()
        
        self.cursor.execute( f"""
                            SELECT Atoms.* 
                            FROM Molecules 
                            JOIN MoleculeAtom ON Molecules.MOLECULE_ID=MoleculeAtom.MOLECULE_ID 
                            JOIN Atoms ON MoleculeAtom.ATOM_ID=Atoms.ATOM_ID 
                            WHERE Molecules.NAME='{name}'
                            ORDER BY Atoms.ATOM_ID ASC 
                            """ )
        theAtoms = self.cursor.fetchall()

        # print(len(theAtoms))
        # print("Atoms From ",name, "____________", theAtoms)
        
        for i, tuple in enumerate(theAtoms):
            mol.append_atom(theAtoms[i][1], theAtoms[i][2], theAtoms[i][3], theAtoms[i][4])

        # print(theAtoms[0])

        self.cursor.execute( f"""
                            SELECT Bonds.* 
                            FROM Molecules 
                            JOIN MoleculeBond ON Molecules.MOLECULE_ID=MoleculeBond.MOLECULE_ID 
                            JOIN Bonds ON MoleculeBond.BOND_ID=Bonds.BOND_ID 
                            WHERE Molecules.NAME='{name}'
                            ORDER BY Bonds.BOND_ID ASC 
                            """ )
        theBonds = self.cursor.fetchall()

        for i, tuple in enumerate(theBonds):
            mol.append_bond(theBonds[i][1], theBonds[i][2], theBonds[i][3])

        return mol
    
    def radius (self):

        self.cursor.execute( "SELECT ELEMENT_CODE FROM Elements ")
        elementCode = self.cursor.fetchall()
        # print(elementCode[0][0])


        self.cursor.execute( "SELECT RADIUS FROM Elements")
        radius = self.cursor.fetchall()
        # print(radius)
        dictionary = {}
        for i, tuple in enumerate(elementCode):
            dictionary.update({elementCode[i][0]:radius[i][0]})

        # print(dictionary)
        return dictionary

    def element_name( self ):
        self.cursor.execute( "SELECT ELEMENT_CODE FROM Elements ")
        elementCode = self.cursor.fetchall()

        self.cursor.execute( "SELECT ELEMENT_NAME FROM Elements")
        name = self.cursor.fetchall()
        
        dictionary = {}
        for i, tuple in enumerate(elementCode):
            dictionary.update({elementCode[i][0]:name[i][0]})

        # print(dictionary)
        return dictionary

    def radial_gradients( self ):
        self.cursor.execute( "SELECT COLOUR1 FROM Elements ")
        colour1 = self.cursor.fetchall()

        self.cursor.execute( "SELECT COLOUR2 FROM Elements ")
        colour2 = self.cursor.fetchall()

        self.cursor.execute( "SELECT COLOUR3 FROM Elements ")
        colour3 = self.cursor.fetchall()

        self.cursor.execute( "SELECT ELEMENT_NAME FROM Elements")
        name = self.cursor.fetchall()

        temp = ""
        for i, tuple in enumerate(name):
            temp += f"""
<radialGradient id="%{name[i][0]}" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
    <stop offset="0%%" stop-color="#%{colour1[i][0]}"/>
    <stop offset="50%%" stop-color="#%{colour2[i][0]}"/>
    <stop offset="100%%" stop-color="#{colour3[i][0]}"/>
</radialGradient>
"""
            
        # print(temp)
        return temp
    

if __name__ == "__main__":
    db = Database(reset=False); # or use default
    MolDisplay.radius = db.radius();
    MolDisplay.element_name = db.element_name();
    MolDisplay.header += db.radial_gradients();
    for molecule in [ 'Water', 'Caffeine', 'Isopentanol' ]:
        mol = db.load_mol( molecule );
        mol.sort();
        fp = open( molecule + ".svg", "w" );
        fp.write( mol.svg() );
        fp.close();






