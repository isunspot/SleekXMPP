from . sleektest import *
from sleekxmpp.xmlstream.stanzabase import ElementBase

class TestElementBase(SleekTest):

    def testExtendedName(self):
        """Test element names of the form tag1/tag2/tag3."""

        class TestStanza(ElementBase):
            name = "foo/bar/baz"
            namespace = "test"

        stanza = TestStanza()
        self.checkStanza(TestStanza, stanza, """
          <foo xmlns="test">
            <bar>
              <baz />
            </bar>
          </foo>
        """)

    def testGetStanzaValues(self):
        """Test getStanzaValues using plugins and substanzas."""

        class TestStanzaPlugin(ElementBase):
            name = "foo2"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            plugin_attrib = "foo2"

        class TestSubStanza(ElementBase):
            name = "subfoo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))

        class TestStanza(ElementBase):
            name = "foo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            subitem = set((TestSubStanza,))

        registerStanzaPlugin(TestStanza, TestStanzaPlugin)

        stanza = TestStanza()
        stanza['bar'] = 'a'
        stanza['foo2']['baz'] = 'b'
        substanza = TestSubStanza()
        substanza['bar'] = 'c'
        stanza.append(substanza)

        values = stanza.getStanzaValues()
        expected = {'bar': 'a',
                    'baz': '',
                    'foo2': {'bar': '',
                             'baz': 'b'},
                    'substanzas': [{'__childtag__': '{foo}subfoo',
                                    'bar': 'c',
                                    'baz': ''}]}
        self.failUnless(values == expected,
            "Unexpected stanza values:\n%s\n%s" % (str(expected), str(values)))


    def testSetStanzaValues(self):
        """Test using setStanzaValues with substanzas and plugins."""

        class TestStanzaPlugin(ElementBase):
            name = "pluginfoo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            plugin_attrib = "plugin_foo"

        class TestStanzaPlugin2(ElementBase):
            name = "pluginfoo2"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            plugin_attrib = "plugin_foo2"

        class TestSubStanza(ElementBase):
            name = "subfoo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))

        class TestStanza(ElementBase):
            name = "foo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            subitem = set((TestSubStanza,))

        registerStanzaPlugin(TestStanza, TestStanzaPlugin)
        registerStanzaPlugin(TestStanza, TestStanzaPlugin2)

        stanza = TestStanza()
        values = {'bar': 'a',
                  'baz': '',
                  'plugin_foo': {'bar': '',
                                 'baz': 'b'},
                  'plugin_foo2': {'bar': 'd',
                                  'baz': 'e'},
                  'substanzas': [{'__childtag__': '{foo}subfoo',
                                  'bar': 'c',
                                  'baz': ''}]}
        stanza.setStanzaValues(values)

        self.checkStanza(TestStanza, stanza, """
          <foo xmlns="foo" bar="a">
            <pluginfoo baz="b" />
            <pluginfoo2 bar="d" baz="e" />
            <subfoo bar="c" />
          </foo>
        """)

    def testGetItem(self):
        """Test accessing stanza interfaces."""

        class TestStanza(ElementBase):
            name = "foo"
            namespace = "foo"
            interfaces = set(('bar', 'baz'))
            sub_interfaces = set(('baz',))

        class TestStanzaPlugin(ElementBase):
            name = "foobar"
            namespace = "foo"
            plugin_attrib = "foobar"
            interfaces = set(('fizz',))

        TestStanza.subitem = (TestStanza,)
        registerStanzaPlugin(TestStanza, TestStanzaPlugin)

        stanza = TestStanza()
        substanza = TestStanza()
        stanza.append(substanza)
        stanza.setStanzaValues({'bar': 'a',
                                'baz': 'b',
                                'foobar': {'fizz': 'c'}})

        # Test non-plugin interfaces
        expected = {'substanzas': [substanza],
                    'bar': 'a',
                    'baz': 'b',
                    'meh': ''}
        for interface, value in expected.items():
            result = stanza[interface]
            self.failUnless(result == value,
                "Incorrect stanza interface access result: %s" % result)

        # Test plugin interfaces
        self.failUnless(isinstance(stanza['foobar'], TestStanzaPlugin),
                        "Incorrect plugin object result.")
        self.failUnless(stanza['foobar']['fizz'] == 'c',
                        "Incorrect plugin subvalue result.")


suite = unittest.TestLoader().loadTestsFromTestCase(TestElementBase)
