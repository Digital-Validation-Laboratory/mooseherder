from pathlib import Path

path_cwd = Path.cwd()
print(path_cwd)

home_dir = Path.home()
print(home_dir)

test_dir = Path.home().joinpath("check").joinpath("this_input.i")
print(test_dir)
#OR
test_dir = Path.home() / "check" / "this_input.i"
print(test_dir)

my_path = Path("/home/lloydf/moose-workdir/mooseherder/scripts/moose-mech-simple.i")
print(my_path)
print()

print(f"Parent: {my_path.parent}")
print(f"Stem: {my_path.stem}")
print(f"Name: {my_path.name}")
print(f"Suffix: {my_path.suffix}")
print()
print(my_path.with_stem('change-moose'))

print(my_path.parent / (str(my_path.stem) +'_out.e'))

print(my_path.is_file())
print(my_path.is_dir())


empty_path = Path()
print(empty_path)
