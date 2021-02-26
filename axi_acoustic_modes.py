"""

"""
import os
import sys
import argparse
import gmsh
import numpy as np


def create_mesh(fileName,cavityType='cylinder',cavityHeight=1,cavityWidth=0.5,meshSize=0.05,display=False):
    print('\n===================== Gmsh INFO =====================\n')
    # Gmsh initialization
    gmsh.initialize()

    # Create new model
    gmsh.model.add("axicavity")

    # Define the profile points and lines 
    if cavityType == 'cylinder':
        gmsh.model.geo.addPoint(meshSize, 0, 0, meshSize, 1)
        gmsh.model.geo.addPoint(meshSize, cavityHeight, 0, meshSize, 2)
        gmsh.model.geo.addLine(1, 2, 1)
        gmsh.model.geo.addPoint((cavityWidth/2) - meshSize, cavityHeight, 0, meshSize, 3)
        gmsh.model.geo.addLine(2,3,2)
        gmsh.model.geo.addPoint((cavityWidth/2) - meshSize, 0, 0, meshSize, 4)
        gmsh.model.geo.addLine(3,4,3)
        gmsh.model.geo.addLine(4,1,4)
        currentLineIdx = 4
    if cavityType == 'ellipsoid':
        gmsh.model.geo.addPoint(meshSize, -cavityHeight/2, 0, meshSize, 1)
        gmsh.model.geo.addPoint(meshSize, cavityHeight/2, 0, meshSize, 2)
        gmsh.model.geo.addLine(1, 2, 1)
        y = np.arange(-cavityHeight/2,cavityHeight/2,meshSize)[::-1]
        x = np.zeros(len(y))
        currentPointIdx = 3
        currentLineIdx = 2
        for idx in range(len(y)):
            x[idx] = meshSize + np.abs(np.sqrt( ((cavityWidth*0.5)**2) * (1-(((y[idx])**2)/((cavityHeight*0.5)**2)))))
            gmsh.model.geo.addPoint(x[idx], y[idx], 0, meshSize, currentPointIdx)
            gmsh.model.geo.addLine(currentPointIdx-1,currentPointIdx,currentLineIdx)
            currentPointIdx += 1
            currentLineIdx += 1
        gmsh.model.geo.addLine(currentPointIdx-1, 1, currentLineIdx)
    if cavityType == 'cone':
        gmsh.model.geo.addPoint(meshSize, 0, 0, meshSize, 1)
        gmsh.model.geo.addPoint(meshSize, cavityHeight, 0, meshSize, 2)
        gmsh.model.geo.addLine(1, 2, 1)
        y = np.arange(0.0,cavityHeight,meshSize)[::-1]
        x = np.zeros(len(y))
        currentPointIdx = 3
        currentLineIdx = 2
        for idx in range(len(y)):
            x[idx] = meshSize + ( (cavityHeight-y[idx])*(cavityWidth/2 - meshSize)/cavityHeight )
            gmsh.model.geo.addPoint(x[idx], y[idx], 0, meshSize, currentPointIdx)
            gmsh.model.geo.addLine(currentPointIdx-1,currentPointIdx,currentLineIdx)
            currentPointIdx += 1
            currentLineIdx += 1
        gmsh.model.geo.addLine(currentPointIdx-1, 1, currentLineIdx)
    #if cavityType == 'custom':
    #    print("CUSTOM OPTION STILL NOT AVAILABLE!")
    
    # Create a curve loop with all the lines
    curveLoop = gmsh.model.geo.addCurveLoop(range(1,currentLineIdx+1), 1)

    # Create a plane surface with the curve loop
    gmsh.model.geo.addPlaneSurface([curveLoop], 1)

    # Synchronization of CAD entities
    gmsh.model.geo.synchronize()

    # Generate a 2D mesh
    gmsh.model.mesh.generate(2)

    # Save mesh as bdf
    gmsh.write("mesh/"+fileName+"_"+cavityType+"_axicavity.bdf")

    # Visualize the model with gmsh GUI
    if '-nopopup' not in sys.argv and display:
        gmsh.fltk.run()

    # Finalize the Gmsh Python API:
    gmsh.finalize()
    return 0


def create_nastran_deck(fileName,cavityType,eigMethod="GIV",harmonicIndex=0,frequencyRange=[20,2000],numberOfEigenvectors=0):
    if not os.path.isdir('nastran_decks/'+fileName+"_n_"+str(harmonicIndex)) :
        os.mkdir('nastran_decks/'+fileName+"_n_"+str(harmonicIndex))
    inputFile = open("mesh/"+fileName+"_"+cavityType+"_axicavity.bdf","rt")
    outputFile = open("nastran_decks/"+fileName+"_n_"+str(harmonicIndex)+"/acoustic_n_"+str(harmonicIndex)+".inp","wt")
    spcList = ""    
    flagSPC = False
    
    outputFile.write("ID ACOUS, MSC\n")
    outputFile.write("APP DISP\n")
    outputFile.write("SOL 3,0\n")
    outputFile.write("TIME 2\n")
    outputFile.write("CEND\n")

    outputFile.write("TITLE = ACOUSTIC CAVITY\n")
    outputFile.write("SUBTITLE = HARMONIC N "+str(harmonicIndex)+"\n")
    outputFile.write("SET 1 = 4\n")
    outputFile.write("METHOD = 11\n")
    if numberOfEigenvectors > 0:
        outputFile.write("OUTPUT\n")
        outputFile.write(" PRES = 1\n")
        outputFile.write(" STRESS = ALL\n")
    outputFile.write("BEGIN BULK\n")
    outputFile.write("AXSLOT  1.225   1.01E5  "+str(harmonicIndex)+"               0\n")

    for line in inputFile:
        tempCard = line[0:8]
        if tempCard == "GRID    ":
            tempLine = "GRIDF   " + line[8:16] + line[24:40]
            outputFile.write(tempLine+"\n")        
        elif tempCard == "CBAR    ":
            tempLine = "CAXIF2  " + line[8:16] + line[24:40]
            if line[16:24] == "2       ":
                spcList += line[24:40]
            outputFile.write(tempLine+"\n")        
        elif tempCard == "CTRIA3  ":
            tempLine = "CAXIF3  " + line[8:16] + line[24:48]
            outputFile.write(tempLine+"\n")        
    if flagSPC:
        outputFile.write("SPC1                    "+spcList+"\n")        
    outputFile.write("EIGR    11      "+eigMethod+"     "+str(float(frequencyRange[0]))+"    "+str(float(frequencyRange[1]))+"  "+"        "+str(numberOfEigenvectors)+"       \n")
#outputFile.write("+AB     MAX\n")    
    outputFile.write("ENDDATA")        
            
    print("\nNastran deck created for "+fileName+" with harmonic index = "+str(harmonicIndex)+" (nastran_decks/"+fileName+"_n_"+str(harmonicIndex)+"/)\n")

    return 0

def run_nastran_case(fileName,harmonicIndex=0):
    print("Running Nastran for harmonic index "+str(harmonicIndex)+" . . .\n")
    os.system('nastran nastran_decks/'+fileName+'_n_'+str(harmonicIndex)+'/acoustic_n_'+str(harmonicIndex)+'.inp')
    print("Run completed for harmonic index "+str(harmonicIndex)+"\n")
    return 0

def extract_eigenvalues(fileName,harmonicIndex=0):
    if not os.path.isdir('results/'+fileName):
        os.mkdir('results/'+fileName)
    filePath = 'nastran_decks/'+fileName+'_n_'+str(harmonicIndex)+'/acoustic_n_'+str(harmonicIndex)+'.inp.out'
    resultsFile = open(filePath,"rt")
    lines = resultsFile.readlines()
    lineNumber = 0
    for line in lines:
        lineNumber += 1
        if 'R E A L   E I G E N V A L U E S' in line:
            break
    outputFile = open('results/'+fileName+'/real_eigenvalues_n_'+str(harmonicIndex)+'.dat', "wt")
    for idx in np.arange(lineNumber,len(lines)):
        if '* * * END OF JOB * * *' in lines[idx]:
            break
        if lines[idx] != '\n':
            outputFile.write(lines[idx])
    print("Eigenvalues for harmonic index "+str(harmonicIndex)+" exported to results/"+fileName+"\n")
    return 0

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-fn","--fileName", help="Choose a file name for the case. Default = 'case'",type=str)
    parser.add_argument("-ct","--cavityType", help="Choose a cavity type among the available options: ['cylinder','ellipsoid','cone']. Default = 'cylinder'",type=str)
    parser.add_argument("-ch", "--cavityHeight", help="Set the cavity height. Default = 1", type=float)
    parser.add_argument("-cw", "--cavityWidth", help="Set the cavity width. Default = 0.5", type=float)
    parser.add_argument("-ms", "--meshSize", help="Set the mesh element size. Default = 0.05", type=float)
    parser.add_argument("-dm", "--displayMesh",nargs='?', help="Display the mesh create in the gmsh GUI", const=True , type=bool)
    parser.add_argument("-fr", "--frequencyRange", help="Frequency range of modal extraction. Default =[20.0,2000.0]")
    parser.add_argument("-hi", "--harmonicIndices", help="Set the maximum harmonic index of azimuthal modes. Default =0",type=int)
    parser.add_argument("-ne", "--numberOfEigenvectors", help="Number of eigenvectors to be exported. Default = 0")
    parser.add_argument("-em", "--eigenMethod", help="Set the method to compute the eigenvalues/vectors. Default = GIV", type=str)
    args = parser.parse_args()
    
    fileName = 'case' if not args.fileName else args.fileName
    cavityType = 'cylinder' if not args.cavityType else args.cavityType
    cavityHeight = 1 if not args.cavityHeight else args.cavityHeight
    cavityWidth = 0.5 if not args.cavityWidth else args.cavityWidth
    meshSize = 0.05 if not args.meshSize else args.meshSize
    displayMesh = False if not args.displayMesh else args.displayMesh
    frequencyRange = [20, 2000] if not args.frequencyRange else args.frequencyRange
    harmonicIndices = 1 if not args.harmonicIndices else args.harmonicIndices
    numberOfEigenvectors = 0 if not args.numberOfEigenvectors else args.numberOfEigenvectors
    eigenMethod = "GIV" if not args.eigenMethod else args.eigenMethod
    
    availableCavityTypes =  ['cylinder','ellipsoid','cone'] # to be added: 'custom' 

    try: 
        assert cavityType in availableCavityTypes, "\n\nINVALID CAVITY TYPE!!! \n\nPlease choose one of the available options: "+str(availableCavityTypes)+"\n\n"
        create_mesh(fileName,cavityType,cavityHeight,cavityWidth,meshSize,displayMesh)
        print('\n===================== Nastran INFO =====================\n')
        for hidx in range(harmonicIndices):
            create_nastran_deck(fileName,cavityType,eigenMethod,hidx,frequencyRange,numberOfEigenvectors)
            run_nastran_case(fileName,hidx)
            extract_eigenvalues(fileName,hidx)

    except AssertionError as msg:  
        print(msg) 

if __name__ == "__main__":
    main(sys.argv[1:])
