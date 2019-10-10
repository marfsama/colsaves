import colsaves.tools as tools

def test_stream_bits_one_byte():
    b = [0]
    assert [0] == list(tools.stream_bits(b,  8))
    assert [0, 0] == list(tools.stream_bits(b,  4))


    b = [15]
    assert [15] == list(tools.stream_bits(b,  8))
    assert [0, 15] == list(tools.stream_bits(b,  4))
    assert [0, 0, 0, 0, 1, 1, 1, 1] == list(tools.stream_bits(b,  1))
    
    b = [240]
    assert [240] == list(tools.stream_bits(b,  8))
    assert [15, 0] == list(tools.stream_bits(b,  4))
    assert [1, 1, 1, 1, 0, 0, 0, 0] == list(tools.stream_bits(b,  1))

    b = [255]
    assert [255] == list(tools.stream_bits(b,  8))
    assert [15, 15] == list(tools.stream_bits(b,  4))
    assert [1, 1, 1, 1, 1, 1, 1, 1] == list(tools.stream_bits(b,  1))

    b = [255] # 111 111 11
    assert [7, 7, 3] == list(tools.stream_bits(b,  3))
    
    b = [227] # 111 0000 11
    assert [7, 0, 3] == list(tools.stream_bits(b,  3))

def test_stream_bits_multiple_bytes():
    b = [0, 0]
    assert [0, 0] == list(tools.stream_bits(b,  8))
    assert [0, 0, 0, 0] == list(tools.stream_bits(b,  4))

    b = [255, 0]
    assert [255, 0] == list(tools.stream_bits(b,  8))
    assert [15, 15, 0, 0] == list(tools.stream_bits(b,  4))

    b = [0, 255]
    assert [0, 255] == list(tools.stream_bits(b,  8))
    assert [0, 0, 15, 15] == list(tools.stream_bits(b,  4))

    b = [227, 142]  #11100 011|10 00111 0
    assert [7, 0, 7, 0, 7, 0] == list(tools.stream_bits(b,  3))
    assert [28, 14, 7,  0] == list(tools.stream_bits(b,  5))
