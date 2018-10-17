#!/bin/bash

# Generate a template test file for each source file

find .. -name '*.py' -print | while read PATHNAME
do
    NAME=$(basename "$PATHNAME")

# exclude these
if [[ "$NAME" =~ (__init__.py|pathhack.py|test_.*) ]] ; then
    echo "EXCLUDING $NAME"
    continue
else
    echo "PROCESSING $NAME"
fi

    IMPORT=$(tr '/' '.' <<< "$PATHNAME" | sed -e 's|^\.*||' -e 's|\.py$||')
    TNAME=${NAME%%.py}
    FOUT="test_$NAME"

#    echo "$NAME -> $FOUT xx $IMPORT yy $NAME2"

    if [ -e "$FOUT" ] ; then
        echo "Skipping existing $FOUT"
        continue
    fi

cat << EOF > "$FOUT"
#!/usr/bin/env python

# TODO this is a generated template test - please update with some real tests

import pathhack
import unittest

import $IMPORT


class Test_$TNAME(unittest.TestCase):

    def test_xxx(self):
        """Test xxx"""
        self.assertEquals(50, 50)

    def test_yyy(self):
        """Test yyy"""
        self.assertEquals(50, 50)


if __name__ == '__main__':
    unittest.main()
EOF

done
