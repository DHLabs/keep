from lxml import etree
import sys

HEADER   = '*[local-name() = "head"]'
BODY     = '*[local-name() = "body"]'
INSTANCE = '//*[local-name() = "instance"]'
TITLE    = '*[local-name() = "title"]'
BINDINGS = '*[local-name() = "bind"]'
TRANSLATIONS = '*[local-name() = "itext"]'


class XFormReader():

    xform_dict = {}
    reference_ids = []

    def __init__( self, xform_file ):
        '''
            Parses an XML XForm in 3 steps.

            1. Parses the XForm header, giving us the model with xpaths we need
               to connect to the body. Also applies bindings to the model.
               Translations are parsed but are not applied until the end of the
               parsing process.

            2. Parse the XForm body, giving us IDs for translations and data
               types if the model bindings did not contain this information.

            3. Finally apply the translations we have to any labels that
               matches the translations IDs used.
        '''

        # Set up our initial xform dictionary
        self.xform_dict = {
            'title': None,
            'children': None,
            'type': 'survey',
            'default_language': 'default'
        }

        # Grab the root element of the xml file
        root = etree.parse( xform_file )
        root = root.getroot()

        # Parse the header
        header = root.xpath( HEADER )[0]
        title, model, translations = self.parse_header( header )

        self.xform_dict[ 'title' ]    = title
        self.xform_dict[ 'children' ] = model

        # Parse the form body
        for el in root:
            if 'body' in el.tag:
                self.parse_body( el )

        # Apply translations we have found
        self.apply_translations( translations )

    def _apply_itext( self, model, tid, lang, value ):
        '''
            Loop through all the fields in the model and apply translations
            where necessary.
        '''
        for field in model:
            if 'children' in field:
                self._apply_itext( field['children'], tid, lang, value )

            # Do we have a label that contains translations?
            if 'label' in field and isinstance( field['label'], dict ):

                # Check if we have a translation for this item
                label = field[ 'label' ]
                if label[ 'tid' ] == tid:
                    label[ lang ] = value

            # Apply translations to choices for selections
            if 'choices' in field:
                self._apply_itext( field[ 'choices' ], tid, lang, value )

            if 'bind' in field:
                binding = field['bind']

                if 'jr:constraintMsg' in binding:

                    if isinstance( binding['jr:constraintMsg'], dict ):

                        label = binding['jr:constraintMsg']
                        if label['tid'] == tid:
                            label[ lang ] = value

                    elif tid == binding['jr:constraintMsg']:
                        label = {'tid': tid, lang: value }
                        binding['jr:constraintMsg'] = label

    def _clean_itext( self, model ):
        '''
            Loop through all the fields in the model and remove translation
            meta data where necessary
        '''
        for field in model:
            if 'children' in field:
                self._clean_itext( field['children'] )

            # Do we have a label that contains translations?
            if 'label' in field and isinstance( field['label'], dict ):
                if 'tid' in field[ 'label' ]:
                    del field['label']['tid']

            if 'jr:constraintMsg' in field and \
                    isinstance( field['jr:constraintMsg'], dict ):
                if 'tid' in field['jr:constraintMsg']:
                    del field['jr:constraintMsg']['tid']

            # Apply translations to choices for selections
            if 'choices' in field:
                self._clean_itext( field[ 'choices' ] )

            if 'bind' in field:
                binding = field['bind']
                if 'jr:constraintMsg' in binding:
                    if isinstance( binding['jr:constraintMsg'], dict ):
                        del binding['jr:constraintMsg']['tid']

    def apply_translations( self, translations ):
        '''
            Apply translations to any labels/constraintMsgs we can find.
        '''
        for lang, trans in translations.items():
            for itext in trans:

                if itext.get( 'id', None ) is None:
                    continue

                tid = "jr:itext('%s')" % ( itext.get( 'id' ) )

                value_element = itext.xpath( '*[local-name() = "value"]' )[0]
                value = self.parse_label( value_element )

                self._apply_itext( self.xform_dict[ 'children' ],
                                   tid, lang, value )

        # Apply itext adds metadata so we can easily find translations. Remove
        # this metadata from the final dictionary.
        self._clean_itext( self.xform_dict[ 'children' ] )

    def parse_body( self, root ):
        '''
            Parse the XForm body. The XForm body provides additional data-type
            information if not present in the bindings and labels for the
            fields in the form.
        '''
        for el in root:
            name       = el.get( 'ref' )
            field_type = el.xpath( 'local-name()' )

            self.set_field( self.xform_dict['children'], name, field_type, el )

            if field_type == 'group':
                self.parse_body( el )

    def parse_header( self, root ):
        '''
            Parse the XForm header pulling out the form title and bindings
        '''
        model        = None

        # Grab the title
        title = root.xpath( TITLE )[0].text

        # Find our model and parse it!
        model_name = '/' + root.xpath( INSTANCE )[0][0].xpath( 'local-name()' )
        model = self.parse_model( root.xpath( INSTANCE )[0][0], model_name )

        translations = {}

        # Parse all the bindings
        for el in root:

            if 'model' == el.xpath( 'local-name()' ):

                for model_el in el:

                    if 'bind' in model_el.tag:
                        # Grab the reference id from the bind and attempt to
                        # find the matching field to bind this information to.
                        name = model_el.get( 'nodeset' )
                        self.set_binding( model, name, model_el )

                    elif 'itext' in model_el.tag:

                        # Loop through each translation list and capture the
                        # translations to be applied later
                        for translation in model_el:
                            lang = translation.get( 'lang' )
                            translations[ lang ] = translation

                            # If the default field is set for this language,
                            # set this language as the default.
                            if translation.get( 'default', None ) is not None:
                                self.xform_dict[ 'default_language' ] = lang

        return title, model, translations

    def parse_model( self, root, name ):
        ''' Parse an XForm model '''
        model = []
        for el in root:
            local_name = el.xpath( 'local-name()' )
            ref_id = name + '/' + local_name
            self.reference_ids.append( ref_id )

            # Set up defaults for the field
            field = { 'type': 'text',
                      'label': local_name,
                      'id': ref_id,
                      'name': local_name }

            # Recurse into a model tag to handle groups correctly
            if len( el.getchildren() ) > 0:
                field[ 'children' ] = self.parse_model( el, ref_id )
                field[ 'type' ] = 'group'

            model.append( field )

        return model

    def parse_type( self, type_str ):
        if type_str == 'select1':
            return 'select one'

        if type_str == 'select':
            return 'select all that apply'

        if type_str == 'binary':
            return 'photo'

        if type_str == 'undefined':
            return 'text'

        if type_str in [ 'int', 'xsd:int' ]:
            return 'integer'

        if type_str == 'xsd:date':
            return 'date'

        if type_str in [ 'string', 'xsd:string' ]:
            return 'text'

        return type_str

    def set_binding( self, model, name, binding ):

        # Attempt to find the model we want to assign these bindings to.
        for field in model:
            if 'children' in field:
                self.set_binding( field[ 'children' ], name, binding )

            if field[ 'id' ] == name:
                field[ 'bind' ] = {}

                # For each bind attribute, add the key/value to our field.
                for key in binding.keys():

                    # Skip over the nodeset attribute
                    if key == 'nodeset':
                        continue

                    value = binding.get( key )

                    # Handle data-types correctly
                    if key == 'type':
                        value = self.parse_type( value )

                        if 'type' in field and field[ 'type' ] == 'note':
                            continue

                        field[ 'type' ] = value
                        continue

                    # Clean up the key and assign the value to our field
                    # bindings
                    key = self._clean_key( key, binding.nsmap )
                    value = self._clean_value( value )
                    field[ 'bind' ][ key ] = value

                # Clean up empty bind fields
                if len( field[ 'bind' ].keys() ) == 0:
                    del field[ 'bind' ]

    def parse_label( self, label ):
        '''
            Labels could possibly have simple strings or a more complex
            combination of outputs from previous questions.
        '''
        label_str = []

        # Do we have translations for this label?
        if label.get( 'ref', None ):
            return { 'tid': label.get( 'ref' ) }

        # Go through each node in the label
        for node in label.xpath( 'node()' ):

            # If the node is simply a string, append and continue
            if isinstance( node, ( str, unicode ) ):
                label_str.append( node )
            # Othewise, figure out what type of output this is and append to
            # the final label string.
            elif isinstance( node, etree._Element ):
                value = self._clean_value( node.get( 'value' ) )
                label_str.append( value )

        return ''.join( label_str )

    def set_field( self, model, name, field_type, root ):

        for field in model:

            if 'children' in field:
                self.set_field( field['children'], name, field_type, root )

            if field[ 'id' ] == name:

                if 'select' in field_type and 'select' not in field['type']:
                    field[ 'type' ] = self.parse_type( field_type )

                for element in root:
                    if 'hint' in element.tag:
                        field[ 'hint' ] = element.text

                    if 'label' in element.tag:
                        field[ 'label' ] = self.parse_label( element )

                    if 'item' in element.tag:
                        choice = {}
                        for val in element:
                            if 'label' in val.tag:
                                choice[ 'label' ] = self.parse_label( val )

                            if 'value' in val.tag:
                                choice[ 'name' ] = val.text

                        if 'choices' not in field:
                            field[ 'choices' ] = []
                        field[ 'choices' ].append( choice )

    def _clean_key( self, attr, nsmap ):
        ''' Replace namespaces with their original marker value. '''
        for key, val in nsmap.items():
            if val in attr:
                return attr.replace( '{%s}' % ( val ), '%s:' % ( key ) )
        return attr

    def _clean_value( self, attr ):
        for ref in self.reference_ids:
            if ref in attr:
                base_name = ref.split( '/' )[-1]
                attr = attr.replace( ref, '${%s}' % ( base_name ) )

        if 'true()' in attr:
            attr = attr.replace( 'true()', 'yes' )

        if 'false()' in attr:
            attr = attr.replace( 'false()', 'no' )

        return attr

    def to_json_dict( self ):
        return self.xform_dict

    def __repr__( self ):
        return str( self.xform_dict )


def main():
    survey = XFormReader( open( sys.argv[1], 'rb' ) )
    return survey


if __name__ == '__main__':
    print main()
