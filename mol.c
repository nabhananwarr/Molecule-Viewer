//Nabhan Anwar, 1200703
#include "mol.h"
#include <math.h>
#define M_PI 3.14159265359

//set an atom's details
void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
    strcpy(atom->element, element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

//get the details from the atom
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    strcpy(element, atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

//set a bond's details
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs ){

    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;
    compute_coords(bond);
}

//get the details from the bond
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom**atoms, unsigned char *epairs ){
    
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms;
    *epairs = bond->epairs;
}

void compute_coords( bond *bond ){
    atom *a1 = &(bond->atoms[bond->a1]);
    atom *a2 = &(bond->atoms[bond->a2]);

    bond->x1 = a1->x;
    bond->x2 = a2->x;

    bond->y1 = a1->y;
    bond->y2 = a2->y;
    //find average z value and then len using distance formula
    bond->z = (a1->z + a2->z)/ 2.0;
    bond->len = sqrt(((a2->x - a1->x) * (a2->x - a1->x)) + ((a2->y - a1->y)*(a2->y - a1->y)));

    bond->dx = (bond->x2 - bond->x1)/bond->len;
    bond->dy = (bond->y2 - bond->y1)/bond->len;
}

//allocates enough memory for a molecule 
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
    molecule * mol = malloc(sizeof(struct molecule));

    //set the atom and bond maxes and then malloc memory for atoms and bonds too
    mol->atom_max = atom_max;
    mol->atom_no = 0;
    mol->atoms = malloc(sizeof(struct atom) * atom_max);
    mol->atom_ptrs = malloc(sizeof(struct atom*) * atom_max);

    mol->bond_max = bond_max;
    mol->bond_no = 0;
    mol->bonds = malloc(sizeof(struct bond) * bond_max);
    mol->bond_ptrs = malloc(sizeof(struct bond*) * bond_max);

    return mol;
}

//copies one molecule to another
molecule *molcopy( molecule *src ){
    molecule * mol = molmalloc(src->atom_max, src->bond_max); 

    //add atoms from source to molecule
    for(int i = 0; i < src->atom_no; i++){
        molappend_atom(mol, &(src->atoms[i]));
    }
    for(int i = 0; i < src->bond_no; i++){
        molappend_bond(mol, &(src->bonds[i]));
    }

    return mol;
}

//frees all the pointers in a molecule and itself 
void molfree( molecule *ptr ){

    free(ptr->atoms);
    free(ptr->bonds);
    free(ptr->atom_ptrs);
    free(ptr->bond_ptrs);
    free(ptr);
}

//adding an atom to a molecule
void molappend_atom( molecule *molecule, atom *atom ){
    
    //realloc if atom_max is equal to atom_no or 0
    if(molecule->atom_max == 0){
        molecule->atom_max = 1;
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
    }
    else if(molecule->atom_no == molecule->atom_max){
        molecule->atom_max = molecule->atom_max * 2;
        molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
    }

    //copy the details from one atom
    strcpy(molecule->atoms[molecule->atom_no].element, atom->element);
    molecule->atoms[molecule->atom_no].x = atom->x; 
    molecule->atoms[molecule->atom_no].y = atom->y; 
    molecule->atoms[molecule->atom_no].z = atom->z; 
    
    molecule->atom_no++;
    //set atom_ptrs to the corresponding atoms
    for(int i = 0; i < molecule->atom_no; i++){ 
        molecule->atom_ptrs[i] = &(molecule->atoms[i]);
    }
}

//adding a bond to a molecule
void molappend_bond( molecule *molecule, bond *bond ){
    
    //realloc if bond_max is equal to bond_no or 0
    if(molecule->bond_max == 0){
        molecule->bond_max = 1;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
    } 
    else if(molecule->bond_no == molecule->bond_max){
        molecule->bond_max = molecule->bond_max * 2;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
    }
    
    //copy the details from the bond
    molecule->bonds[molecule->bond_no].a1 = bond->a1; 
    molecule->bonds[molecule->bond_no].a2 = bond->a2;
    molecule->bonds[molecule->bond_no].epairs = bond->epairs;
    molecule->bonds[molecule->bond_no].x1 = bond->x1;
    molecule->bonds[molecule->bond_no].y1 = bond->y1;
    molecule->bonds[molecule->bond_no].x2 = bond->x2;
    molecule->bonds[molecule->bond_no].y2 = bond->y2;
    molecule->bonds[molecule->bond_no].len = bond->len;
    molecule->bonds[molecule->bond_no].dx = bond->dx;
    molecule->bonds[molecule->bond_no].dy = bond->dy;
    
    molecule->bond_no++;
    for(int i = 0; i < molecule->bond_no; i++){ 
        molecule->bond_ptrs[i] = &(molecule->bonds[i]);
    }
    //test: printf("*****%f  %f  %f  %f  %f  %f  %f*****\n", molecule->bonds[0].x1, molecule->bonds[0].y1, molecule->bonds[0].x2, molecule->bonds[0].y2, molecule->bonds[0].len, molecule->bonds[0].dx, molecule->bonds[0].dy);
}

//compar function for atoms
int atom_z_comp( const void *a, const void *b ){
    struct atom **a_ptr, **b_ptr;
    a_ptr = (atom **)a;
    b_ptr = (atom **)b;
    
    //compare z values between atoms
    int val = 0;
    if((*a_ptr)->z > (*b_ptr)->z){
        val = 1;
    }
    else if((*a_ptr)->z < (*b_ptr)->z){
        val = -1;
    }
    else{
        val = 0;
    }
    return val;
}
//compar function for bonds
int bond_z_comp( const void *a, const void *b ){
    struct bond **a_ptr, **b_ptr;
    a_ptr = (bond **)a;
    b_ptr = (bond **)b;
    
    //compare z averages for bonds
    double z = (*a_ptr)->z - (*b_ptr)->z;

    if(z < 0.0){
        return -1;
    }
    else if(z >0.0){
        return 1;
    }
    else{
        return 0;
    }

}
//sorting function
void molsort( molecule *molecule ){
    //sotring the atoms by z values
    qsort( molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom *), atom_z_comp );
    qsort( molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond *), bond_z_comp );
}

//x, y, z matrix-making functions 
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(deg * M_PI / 180);
    xform_matrix[1][2] = -sin(deg * M_PI / 180);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(deg * M_PI / 180);
    xform_matrix[2][2] = cos(deg * M_PI / 180);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    xform_matrix[0][0] = cos(deg * M_PI / 180);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(deg * M_PI / 180);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(deg * M_PI / 180);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(deg * M_PI / 180);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    xform_matrix[0][0] = cos(deg * M_PI / 180);
    xform_matrix[0][1] = -sin(deg)* M_PI / 180;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(deg* M_PI / 180);
    xform_matrix[1][1] = cos(deg* M_PI / 180);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

//transforms the x, y, z values of the atoms
void mol_xform( molecule *molecule, xform_matrix matrix ){

    int x = molecule->atoms->x;
    int y = molecule->atoms->y;
    int z = molecule->atoms->z;

    molecule->atoms->x = matrix[0][0]*x + matrix[0][1]*x + matrix[0][2]*x;
    molecule->atoms->y = matrix[1][0]*y + matrix[1][1]*y + matrix[1][2]*y;
    molecule->atoms->z = matrix[2][0]*z + matrix[2][1]*z + matrix[2][2]*z;

    for (int i = 0; i < molecule->bond_no; i++){
        compute_coords( &molecule->bonds[i]);
    }
}

