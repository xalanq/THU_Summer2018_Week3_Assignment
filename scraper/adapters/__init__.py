__all__ = [
    "adapter_people",
    "adapter_xinhua"
]

from . import *


def getAdapters():
    return [
        adapter_people.AdapterPeople(),
        adapter_xinhua.AdapterXinhua()
    ]

def main():
    pass


if __name__ == '__main__':
    main()