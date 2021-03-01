from array import array

def prefix(file,prefix_names,prefix_links): #print prefixes
    j=0
    for x in prefix_names:
        file.write("@prefix %s: <%s>.\n" %(x,prefix_links[j]))
        j=j+1

def uri(file,numuri): #baseURI
    file.write("#baseURI: %s%d \n" %(baseURI,numuri))

def find_target (line,p):
    for word in line.split():
        if word != '@forAll':
            if p == 0:
                p = p + 1
                word = word.replace(':', '')
                word = word.replace(',', '')
                targetclass = word.capitalize()
                target = word
                return target,targetclass

def declaration(file,uri):  #create declaration
    file.write("<%s%d>\n" % (baseURI,uri_number))
    file.write("\ta owl:Ontology ;\n")
    file.write("\towl:imports sh: ;\n")
    file.write("\tsh:declare xsd:PrefixDeclaration ;\n")
    j = 0
    for x in prefix_names:
        file.write("\tsh:declare[\n")
        file.write("\t\ta sh:PrefixDeclaration ;\n")
        file.write("\t\tsh:namespace \"%s\" ^^xsd:anyURI ;\n" % prefix_links[j])
        file.write("\t\tsh:prefix \"%s\" ;\n" % x)
        file.write("\t] ;\n")
        j = j + 1
    file.write(".\n")

def Shapes(file, uri): #create Shapes
    file.write("%s:N3RulesShape_%d\n" % (myprefix, int(i)))
    file.write(("\ta sh:NodeShape ;\n"))
    file.write("\tdc:description \"The node shape that holds the rule\" ;\n")
    file.write("\trdfs:isDefinedBy <%s%d> ;\n" % (baseURI,uri))
    file.write("\trdfs:label \"A rule.\";\n")
    file.write("\tsh:rule %s:SPARQLRule_%d ;\n" % (myprefix, int(i)))
    file.write("\tsh:targetClass %s:%s ;\n" % (myprefix, targetclass))
    file.write(".\n")
    file.write("%s:SPARQLRule_%d \n" % (myprefix, int(i)))
    file.write(("\ta sh:SPARQLRule ;\n"))
    file.write("\trdfs:isDefinedBy <%s%d> ;\n" % (baseURI,uri))
    file.write("\trdfs:label \"A rule\";\n")

def construct(file,string,target):  #CONSTRUCT
    file.write("\tsh:construct\"\"\" CONSTRUCT { ")
    for word in string.split():
        word = word.replace('.', ' ')
        if word.startswith(':') or word.startswith('{:'):
            word = word.replace(':', '?')
        targetword = word.replace('?', '')
        targetword = targetword.replace('{?', '')
        targetword = targetword.replace('{', '')
        targetword = targetword.replace('}', '')
        if targetword == target:
            file.write(" $this ")
        else:
            file.write(word + ' ')

def where_variables(file,string,target,targetclass): #WHERE , declare classes of the variables
    for word in string.split():  # forAll
        if word != '@forAll':
            word = word.replace(',', '')
            word = word.replace('.', '')
            word = word.replace(':', '')
            if word == target:
                file.write("\t$this a %s:" % myprefix + targetclass + '.\n')
            else:
                file.write("\t?%s a %s:" % (word, myprefix) + word.capitalize() + '.\n')

def where_conditions(file,string,target): #WHERE
    for word in string.split():
        if word.startswith(':') or word.startswith('{:'):
            word = word.replace(':', '')
            word = word.replace('{', '')
        word = word.replace('}', '')
        if word == target:
            file.write("\t$this")
        else:
            if myprefix in word:  # if the prefix is contained then this is the predicate
                file.write("\t%s" % word)
            elif '\"' in word:  # datatype string
                word = word.replace('\"', '')
                file.write("\t\\\"%s\"\\" % word)
            else:
                file.write("\t?%s" % word)

def close_rules(file,order,baseURI,number):
    file.write(" }\"\"\";")
    file.write("\n\n")
    file.write("sh:order %d;\n" % order)
    file.write("sh:prefixes <%s%d> ;\n" % (baseURI, number))
    file.write(".\n\n")

#open a txt file
f = open("n3.txt", "r")
#create a txt output file
outF = open("ShaclRules_Collection.txt", "w")

uri_number=0
collection_uri=0
#baseURI
baseURI="http://convertN3ToShacl/1."
uri(outF,collection_uri)
prefix_names=[]
prefix_links=[]

k=0
for line in f.readlines():
    if '@prefix' in line:
        pfirst, pmiddle, prest = line.partition(":")
        pfirst = pfirst.replace("@prefix", "")
        pfirst = pfirst.replace(" ", "")
        prefix_names.append(pfirst)
        prest = prest.replace(">.", '')
        prest = prest.replace("<", "")
        prest = prest.replace(" ", "")
        prest = prest.replace("\n", "")
        prefix_links.append(prest)
    if k == 0:
        myprefix = pfirst
    k=k+1

prefix(outF,prefix_names,prefix_links)
declaration(outF,collection_uri)

f.seek(0) #move the cursor to the beginning of the file
order=0

i=0
for line in f.readlines():
    p = 0
    if '@forAll' in line:
        target,targetclass=find_target(line,p)
    if 'log:implies' not in line:
        if '@prefix' not in line:
            outF.write(line)
    elif 'log:implies' in line:
        i=i+1 #counting the number of shacl shape nodes
        outRule = open("ShaclRule_%s.txt" %i,'w')  #create new file for every rule
        uri_number=uri_number+1
        uri(outRule,uri_number)
        prefix(outRule, prefix_names, prefix_links)
        declaration(outRule,uri_number) #write declaration in the new files
        Shapes(outRule,uri_number) #write Shapes in the new seperate files
        Shapes(outF,collection_uri) #write shapes in the common file
        first, middle, rest = line.partition("log:implies")
        construct(outF,rest,target)
        construct(outRule,rest,target)
        outF.write("\nWHERE\n{")
        outRule.write("\nWHERE\n{")
        first,middle,rest=first.partition("{")
        where_variables(outF,first,target,targetclass)
        where_variables(outRule, first, target, targetclass)
        first,middle,rest=rest.partition(".")
        where_conditions(outF, first, target)
        where_conditions(outRule, first, target)
        outF.write(middle)
        outRule.write(middle)
        outF.write('\n')
        outRule.write('\n')
        where_conditions(outF, rest, target)
        where_conditions(outRule, rest, target)
        order = order + 1
        close_rules(outF,order,baseURI,collection_uri)
        close_rules(outRule, order, baseURI, uri_number)

f.close()
outF.close()