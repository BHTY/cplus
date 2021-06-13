"""C-Plus Compiler
Version 0.1.0
6/12/2021

Features to Add
- Standard Library
- Operator overloading
"""

import re
import sys

def tokenize(string):
    return re.findall("[a-zA-Z][a-zA-Z0-9]*|==|!=|>=|<=|&&|\\|\\||_?\\d+|[+\-*/=!<>()[\\]{},.;:&\\|]|'.'|\".*\"",string)

def procClass(string):
    finalString = []
    className = string[1]

    #find the beginning of the constructor, create the struct    
    for i in range(len(string)):
        if string[i+1] == className and string[i+2] == "(":
            constructorBeginning = i
            break
        
    toks = string[3:constructorBeginning]
    finalString.append("struct")
    finalString.append(className)
    finalString.append("{")
    
    for i in toks:
        finalString.append(i)
        
    finalString.append("}")
    finalString.append(";")

    #process the constructor header
    constructorHeaderEnding = 0
    i = constructorBeginning
    
    while i < len(string):
        if string[i] == "{": break
        i += 1
    constructorHeaderEnding = i
    constructorHeader = string[constructorBeginning:constructorHeaderEnding]
    newConstructorHeader = [constructorHeader[0], "__{}Constructor".format(className),
                            "(", className, "*", "this", ","]
    newConstructorHeader += constructorHeader[3:]

    #find the end of the constructor and process from there
    constructorEnding = 0
    i = constructorHeaderEnding
    depth = 0
    firstBracket = 0

    while i < len(string):
        if string[i] == "{":
            depth += 1
            firstBracket = 1
        if string[i] == "}":
            depth -= 1
        if depth == 0 and firstBracket:
            break
        i += 1
    constructorEnding = i+1
    constructorBody = string[constructorHeaderEnding:constructorEnding]

    for i in range(len(constructorBody)):
        if constructorBody[i] == "this": constructorBody[i] = "(*this)"

    finalString += newConstructorHeader + constructorBody
    
    #find each successive function
    i = constructorEnding

    while i < len(string):
        #find function header
        try:
            if string[i+2] == "(": #function found
                #find header
                methodHeaderBeginning = i
                methodHeaderEnding = i

                while methodHeaderEnding < len(string):
                    if string[methodHeaderEnding] == "{": break
                    methodHeaderEnding += 1                

                #process header - allow for multi-token return types
                oldHeader = string[methodHeaderBeginning:methodHeaderEnding]
                newHeader = [oldHeader[0], "__{}_{}".format(className, string[i+1]),
                            "(", className, "*", "this", ","]
                newHeader += oldHeader[3:]
                
                #find end of body
                methodEnding = methodHeaderEnding
                depth = 0
                firstBracket = 0

                while methodEnding < len(string):
                    if string[methodEnding] == "{":
                        depth += 1
                        firstBracket = 1
                    if string[methodEnding] == "}":
                        depth -= 1
                    if depth == 0 and firstBracket:
                        break
                    methodEnding += 1
                methodEnding += 1

                #process body
                methodBody = string[methodHeaderEnding:methodEnding]

                for index in range(len(methodBody)):
                    if methodBody[index] == "this": methodBody[index] = "(*this)"

                #add everything together and set i to the end of body variable
                totalMethod = newHeader + methodBody                
                finalString += totalMethod
                i = methodEnding
        
            else: i += 1

        except: i += 1
    
    return finalString, className

def preproc(string): ##import directives to include object-oriented code implemented here
    string = string.split("\n")
    newString = ""

    for i in range(len(string)):
        line = string[i].split(" ")

        if line[0] == "#import":
            file = open(line[1], "r+")
            string[i] = file.read()
            file.close()

    for i in string:
        newString += i + "\n"
    
    return newString

def transpile(string, classNames = [], objNames = []):
    string = tokenize(string)
    finalString = []
    i = 0
    reference = {}

    while i < len(string):
        if string[i] == "class": #find the end of the class and start PROCESSING
            oldI = i
            depth = 0
            firstBracket = 0
            while i < len(string):
                if string[i] == "{":
                    depth += 1
                    firstBracket = 1
                if string[i] == "}":
                    depth -= 1
                if depth == 0 and firstBracket:
                    break
                i += 1
            i += 1
            classInfo = procClass(string[oldI:i])
            finalString += classInfo[0]
            classNames.append(classInfo[1])

        if string[i] in classNames: #recursive algorithm for method calls inside object creation
            endOfStatement = i
            
            while endOfStatement < len(string):
                if string[endOfStatement] == ";": break
                endOfStatement += 1

            objNames.append(string[i+1])
            reference[string[i+1]] = string[i]
            newStatement = [string[i], string[i+1], ";"] #constructor args begin at fourth token
            newStatement += ["__{}Constructor".format(string[i]), "(", "&{}".format(string[i+1]), ","]
            newStatement += string[(i+3):endOfStatement+1]
            i = endOfStatement+1
            finalString += newStatement


        if string[i] in objNames: #add support for accessing/changing variables
            endOfStatement = i

            while endOfStatement < len(string):
                if string[endOfStatement] == ";": break
                endOfStatement += 1

            #construct new function statement - method name is at token two
            if string[i+3] == "(":
                newStatement = ["__{}_{}".format(reference[string[i]], string[i+2]), "(", "&{}".format(string[i]), ","]
                newStatement += string[(i+4):(endOfStatement+1)]
                i = endOfStatement
                finalString += newStatement
            else:
                finalString.append(string[i])

            
        
        else:
            finalString.append(string[i])
        i += 1
 

    return finalString#, classNames, objNames

def toString(lst):
    string = ""

    for i in lst:
        string += i

    return string

def prettyprint_old(string):
    for i in string:
        print(i, end=" ")
        if i == ";" or i == "{" or i == "}": print("")
    return

def prettyprint(string):
    depth = 0
    for i in string:
        print(i, end=" ")
        
        if i == "{":
            depth += 1
        if i == "}":
            depth -= 1
        if i == ";" or i == "}" or i == "{": print("\n" + ("    " * depth), end = "")
    return


string = """
class Person{
	char* name;
	int age;

	void Person(char* name, int age){
		this.name = (char*)malloc(strlen(name));
		strcpy(this.name, name);
		this.age = age;
	}

	void hello(){
		printf("Hello, I'm %s and I'm %d!", this.name, this.age);
	}

}

int main(){
	Person Will("Will", 15);
	Will.hello();
}"""

newstring = """#import Person.cp
int main(){
	Person Will("Will", 15);
	Will.hello();
}
"""


nextstring = """
class Number{
    int value;

    void Number(int value){
        this.value = value;
    }

    void changeValue(int value){
        this.value = value;
    }

    void print(){
        printf("%d", this.value);
    }
    int getValue(){
        return this.value;
    }
}

int main(){
    Number One(1);
    One.print();
    One.changeValue(2);
    One.print();
    int num = One.value + One.getValue() + One.getValue();
}
"""

test = """
class Person{
	char* name;
	int age;

	void Person(char* name, int age){
		this.name = (char*)malloc(strlen(name));
		strcpy(this.name, name);
		this.age = age;
	}

	void hello(){
		printf("Hello, I'm %s and I'm %d!", this.name, this.age);
	}

	char getName(){
            return this.name;
	}

}

int main(){
	Person Will("Will", 15);
	Person Jill(Will.getName(), 15);
}"""
