import os
import PyOpenColorIO as OCIO


__version__ = "0.1.0"


def build_config(output_path):
    """Generate OCIO config"""
    config = OCIO.Config()
    config.setSearchPath(":".join(["luts", "mtx"]))

    # add colorspaces
    config.addColorSpace(aces_colorspace())
    config.addColorSpace(flog_colorspace())
    config.addColorSpace(ncd_colorspace())

    # add displays
    display_spaces = [
        ["F-Log", "flog", ""],
        ["No LUT", "ncd", ""],
    ]
    for name, colorspace, look in display_spaces:
        config.addDisplay("default", name, colorspace, look)

    config.setActiveViews(",".join(["No LUT", "F-Log"]))
    config.setActiveDisplays(",".join(["default"]))

    # set roles
    config.setRole(OCIO.Constants.ROLE_SCENE_LINEAR, "aces")
    config.setRole(OCIO.Constants.ROLE_REFERENCE, "aces")
    config.setRole(OCIO.Constants.ROLE_DATA, "ncd")
    config.setRole(OCIO.Constants.ROLE_DEFAULT, "ncd")
    config.setRole(OCIO.Constants.ROLE_COLOR_PICKING, "ncd")
    config.setRole(OCIO.Constants.ROLE_TEXTURE_PAINT, "flog")
    config.setRole(OCIO.Constants.ROLE_MATTE_PAINT, "flog")
    config.setRole(OCIO.Constants.ROLE_COLOR_TIMING, "flog")
    config.setRole(OCIO.Constants.ROLE_COMPOSITING_LOG, "flog")

    config.sanityCheck()

    with open(output_path, "w") as fhandle:
        fhandle.write(config.serialize())
    print("Wrote {} successfully".format(output_path))


def aces_colorspace():
    """The Academy Color Encoding System reference color space (ACES 2065-1)"""
    col_space = OCIO.ColorSpace(name="aces", family="ACES")
    col_space.setDescription(
        "The Academy Color Encoding System reference color space (ACES 2065-1)"
    )
    col_space.setBitDepth(OCIO.Constants.BIT_DEPTH_F32)
    col_space.setAllocationVars([-8.0, 5.0, 0.00390625])
    col_space.setAllocation(OCIO.Constants.ALLOCATION_LG2)
    return col_space


def flog_colorspace():
    """Fujifilm F-Log color space"""
    col_space = OCIO.ColorSpace(name="flog", family="Fujifilm")
    col_space.setDescription("Fujifilm F-Log color space")
    col_space.setBitDepth(OCIO.Constants.BIT_DEPTH_F32)
    col_space.setAllocationVars([0, 1])
    col_space.setAllocation(OCIO.Constants.ALLOCATION_UNIFORM)
    group_xform = OCIO.GroupTransform()
    group_xform.push_back(
        OCIO.FileTransform(
            "flog_to_linear.cube",
            interpolation=OCIO.Constants.INTERP_LINEAR,
            direction=OCIO.Constants.TRANSFORM_DIR_FORWARD,
        )
    )
    group_xform.push_back(
        OCIO.FileTransform(
            "rec2020_to_ap0.cat02.spimtx",
            direction=OCIO.Constants.TRANSFORM_DIR_FORWARD,
        )
    )
    col_space.setTransform(group_xform, OCIO.Constants.COLORSPACE_DIR_TO_REFERENCE)
    return col_space


def ncd_colorspace():
    """Non-color data"""
    col_space = OCIO.ColorSpace(name="ncd", family="Data")
    col_space.setDescription("Non-color data")
    col_space.setBitDepth(OCIO.Constants.BIT_DEPTH_F32)
    col_space.setIsData(True)
    return col_space


def main():
    """Main function"""
    this_dir = os.path.abspath(os.path.dirname(__file__))
    output_path = os.path.join(this_dir, "config.ocio")
    build_config(output_path)


if __name__ == "__main__":
    main()
