from spock.vector import CartesianVector


def test_cartesianvector_add():
    v1 = CartesianVector(-1, 2, 1)

    v2 = v1 + v1

    # make sure they are not the same object
    assert v2 is not v1

    assert len(v2) == 3
    assert v2[0] == -2
    assert v2[1] == 4
    assert v2[2] == 2


def test_cartesianvector_iadd():
    v1 = CartesianVector(-1, 2, 1)

    vbackup = v1
    v1 += v1

    # make sure same object
    assert v1 is vbackup

    assert len(v1) == 3
    assert v1[0] == -2
    assert v1[1] == 4
    assert v1[2] == 2


def test_cartesianvector_sub():
    v1 = CartesianVector(-1, 2, 5)
    v2 = CartesianVector(5, 4, 3)
    v3 = v1 - v2

    # make sure they are not the same object
    assert v3 is not v1
    assert v3 is not v2

    assert len(v3) == 3
    assert v3[0] == -6
    assert v3[1] == -2
    assert v3[2] == 2


def test_cartesianvector_isub():
    v1 = CartesianVector(-1, 2, 5)
    v2 = CartesianVector(5, 4, 3)

    vbackup = v1
    v1 -= v2

    # make sure same object
    assert v1 is vbackup
    assert v1 is not v2

    assert len(v1) == 3
    assert v1[0] == -6
    assert v1[1] == -2
    assert v1[2] == 2


def test_cartesianvector_mul():
    v1 = CartesianVector(1, 2)

    v2 = v1 * 2

    assert v2 is not v1

    assert len(v2) == 2
    assert v2[0] == 2
    assert v2[1] == 4


def test_cartesianvector_imul():
    v1 = CartesianVector(1, 2)

    vbackup = v1
    v1 *= 2

    assert v1 is vbackup

    assert len(v1) == 2
    assert v1[0] == 2
    assert v1[1] == 4


def test_cartesianvector_div():
    v1 = CartesianVector(1, 4)

    v2 = v1 / 2

    assert v2 is not v1

    assert len(v2) == 2
    # because we 'from __future__ import division' in vector.py
    # py2 and py3 should be the same
    assert v2[0] == 0.5
    assert v2[1] == 2.0


def test_cartesianvector_idiv():
    v1 = CartesianVector(1, 4)

    vbackup = v1
    v1 /= 2

    assert v1 is vbackup

    assert len(v1) == 2
    # because we 'from __future__ import division' in vector.py
    # py2 and py3 should be the same
    assert v1[0] == 0.5
    assert v1[1] == 2.0
