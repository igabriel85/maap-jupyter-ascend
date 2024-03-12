'''
Created on Tue Sep 17 2018

@author: tkososko
'''
from properties.p import Property

#### get properties in dictionnary
prop=Property()
prop_dict=prop.load_property_files('/projects/my-hello-world-project/conf/configuration.properties')



resultat=int(prop_dict['var1']) *int( prop_dict['var2'])
print("The operation =  "+prop_dict['var1']+ " * " + prop_dict['var2'] + " is : ")
print(resultat)

# Output

# OrderedDict([('foo', 'I am awesome'), ('bar', 'fudge-bar'), ('chocolate', 'fudge'),
# ('long', 'a very long property that is described in the property file which takes up multiple lines can be defined by the escape character as it is done here'),
# ('url', 'example.com/api?auth_token=xyz')])