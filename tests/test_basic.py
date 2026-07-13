import resourcetree as rt



def test_tree():


    root = rt.Container("root")


    home = rt.Container(
        "home",
        root
    )


    file = rt.Asset(
        "hello.txt",
        home,
        data="hello"
    )