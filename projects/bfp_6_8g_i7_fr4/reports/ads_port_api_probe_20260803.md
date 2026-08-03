# ADS Python API Probe

Generated: 2026-08-03T00:04:19
Python: `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe`
Keywords: `port, gnd, ground, reference, term, terminal, pin, em, setup, layer`

## Keyword Child Modules

### `keysight.ads.ael`
- `keysight.ads.ael._ael_support`
- `keysight.ads.ael._setup_environment`
- `keysight.ads.ael._setup_support`
- `keysight.ads.ael._wrapping`

### `keysight.ads.de`
- `keysight.ads.de._extension_setup`
- `keysight.ads.de._lazy_import`
- `keysight.ads.de._nameditemcollection`
- `keysight.ads.de._oalibs_support`
- `keysight.ads.de._smart_package_support`
- `keysight.ads.de._wrapping`
- `keysight.ads.de.db._layer_id`
- `keysight.ads.de.experimental.preferences`
- `keysight.ads.de.experimental.thermal_export`

### `keysight.ads.emtools`
- `keysight.ads.emtools._emtools`
- `keysight.ads.emtools._setup_environment`
- `keysight.ads.emtools._setup_support`

## API Hits

### `keysight.ads.ael`

_No keyword hits._

### `keysight.ads.de`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.ArcOrientation` | class | `` | Defines the orientation of an arc or sequence of points. Members: CLOCKWISE : 'Clockwise': The orientation is clockwise. ZERO : 'Zero': The orientation is unspecified or we don't care. COUNTER_CLOCKWISE : 'CounterCloc... |
| `keysight.ads.de.ArcOrientation.CLOCKWISE` | ArcOrientation | `` | Defines the orientation of an arc or sequence of points. Members: CLOCKWISE : 'Clockwise': The orientation is clockwise. ZERO : 'Zero': The orientation is unspecified or we don't care. COUNTER_CLOCKWISE : 'CounterCloc... |
| `keysight.ads.de.ArcOrientation.COUNTER_CLOCKWISE` | ArcOrientation | `` | Defines the orientation of an arc or sequence of points. Members: CLOCKWISE : 'Clockwise': The orientation is clockwise. ZERO : 'Zero': The orientation is unspecified or we don't care. COUNTER_CLOCKWISE : 'CounterCloc... |
| `keysight.ads.de.ArcOrientation.ZERO` | ArcOrientation | `` | Defines the orientation of an arc or sequence of points. Members: CLOCKWISE : 'Clockwise': The orientation is clockwise. ZERO : 'Zero': The orientation is unspecified or we don't care. COUNTER_CLOCKWISE : 'CounterCloc... |
| `keysight.ads.de.BendStyle` | class | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.ADAPTIVE_MITERED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.CURVED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.EXACT_MITERED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.MITERED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.NEW_MITERED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.ROUNDED` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BendStyle.SQUARE` | BendStyle | `` | Defines the style of a bend in a polyline or polygon. Members: SQUARE : 'Square': The bend has square corners. CURVED : 'Curved': The bend has curved corners with a specified radius. MITERED : 'Mitered': The bend has ... |
| `keysight.ads.de.BoxF.TFloatTuple` | GenericAlias | `(iterable=(), /)` | Built-in immutable sequence. If no argument is given, the constructor returns an empty tuple. If iterable is specified the tuple is initialized from iterable's items. If the argument is a tuple, the return value is th... |
| `keysight.ads.de.CapStyle` | class | `` | Defines the style of polyline end caps. Members: SQUARE : 'Square': The end cap is square. ROUND : 'Round': The end cap is round. SQUARE_EXTENDED : 'SquareExtended': The end cap is square and extended by half the widt... |
| `keysight.ads.de.CapStyle.CHAMFER` | CapStyle | `` | Defines the style of polyline end caps. Members: SQUARE : 'Square': The end cap is square. ROUND : 'Round': The end cap is round. SQUARE_EXTENDED : 'SquareExtended': The end cap is square and extended by half the widt... |
| `keysight.ads.de.CapStyle.ROUND` | CapStyle | `` | Defines the style of polyline end caps. Members: SQUARE : 'Square': The end cap is square. ROUND : 'Round': The end cap is round. SQUARE_EXTENDED : 'SquareExtended': The end cap is square and extended by half the widt... |
| `keysight.ads.de.CapStyle.SQUARE` | CapStyle | `` | Defines the style of polyline end caps. Members: SQUARE : 'Square': The end cap is square. ROUND : 'Round': The end cap is round. SQUARE_EXTENDED : 'SquareExtended': The end cap is square and extended by half the widt... |
| `keysight.ads.de.CapStyle.SQUARE_EXTENDED` | CapStyle | `` | Defines the style of polyline end caps. Members: SQUARE : 'Square': The end cap is square. ROUND : 'Round': The end cap is round. SQUARE_EXTENDED : 'SquareExtended': The end cap is square and extended by half the widt... |
| `keysight.ads.de.Cell` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for Library, Cell, and View. Library, Cell and View are part of the Data Management System and are containers for files (known as DMFiles). Each instance represents not only the library, cell or view, but a... |
| `keysight.ads.de.CellviewRef.cell` | property | `` | The referenced cell. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.cell_name` | property | `` | The name of the referenced cell. Read-only. Might be empty if not specified. |
| `keysight.ads.de.CellviewRef.lib` | property | `` | The referenced library. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.lib_name` | property | `` | The name of the referenced library. Read-only. Might be empty if not specified. |
| `keysight.ads.de.CellviewRef.view` | property | `` | The referenced view. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.view_name` | property | `` | The name of the referenced view. Read-only. Might be empty if not specified. |
| `keysight.ads.de.DerivedLayer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a derived layer. A derived layer is a (virtual) layer that is formed by operations on shapes from one or more other layers. Derived layers typically don't have any shapes. |
| `keysight.ads.de.DerivedLayer.abbreviation` | property | `` |  |
| `keysight.ads.de.DerivedLayer.create_boolean_layer` | function | `(tech: 'Tech', layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, layer2: keysight.ads.de.tech._tech.Layer \| str) -> 'DerivedLayer'` | Create a derived layer from two source layers and boolean operation. The derived layer contains all the shapes that result by performing the boolean operation on all the shapes from the two source layers. |
| `keysight.ads.de.DerivedLayer.create_sizing_layer` | function | `(tech: 'Tech', layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, distance: int) -> 'DerivedLayer'` | Create a derived layer from a single source layer, a sizing operation, and a distance parameter. The derived layer contains all the shapes that result by performing the sizing operation on all the shapes from the sour... |
| `keysight.ads.de.DerivedLayer.get_distance_param` | function | `(self) -> int` | Return the distance parameter from this derived layer. This only works for derived layers that use a sizing operation. If you call this function on a derived layer that does not have a distance parameter, it will rais... |
| `keysight.ads.de.DerivedLayer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.DerivedLayer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.DerivedLayer.layer1` | property | `` |  |
| `keysight.ads.de.DerivedLayer.layer1_num` | property | `` |  |
| `keysight.ads.de.DerivedLayer.layer2` | property | `` |  |
| `keysight.ads.de.DerivedLayer.layer2_num` | property | `` |  |
| `keysight.ads.de.DerivedLayer.layer_binding` | property | `` |  |
| `keysight.ads.de.DerivedLayer.library` | property | `` |  |
| `keysight.ads.de.DerivedLayer.name` | property | `` |  |
| `keysight.ads.de.DerivedLayer.number` | property | `` |  |
| `keysight.ads.de.DerivedLayer.operation` | property | `` | Returns the derived layer operation. NOTE: If this is a user defined operation (USER_DEFINED), you must use operation_name to get the name of the operation. |
| `keysight.ads.de.DerivedLayer.operation_name` | property | `` | Returns the name of the derived layer operation. |
| `keysight.ads.de.DerivedLayer.process_role` | property | `` |  |
| `keysight.ads.de.DerivedLayer.tech` | property | `` |  |
| `keysight.ads.de.DMContainer` | class | `()` | Base class for Library, Cell, and View. Library, Cell and View are part of the Data Management System and are containers for files (known as DMFiles). Each instance represents not only the library, cell or view, but a... |
| `keysight.ads.de.DMData.open` | function | `(owner: 'DMContainer', mode: str) -> 'DMData'` | Open a DM database for the given owner. The mode determines how the database is opened: "r" - Open the database read-only. The database must exist. "a" - Open the database for appending data or create a new one. "w" -... |
| `keysight.ads.de.DMFile.lock_file` | function | `(self) -> bool` | Attempt to lock the file and return True if successful. |
| `keysight.ads.de.DMLockStatus` | class | `` | Defines the lock status of a DMFile (file in a Library, Cell or View). Members: NOT_LOCKED : 'NotLocked': The file is not locked. LOCKED_BY_CURRENT_PROCESS : 'LockedByCurrentProcess': The file is locked by the current... |
| `keysight.ads.de.DMLockStatus.LOCKED_BY_CURRENT_PROCESS` | DMLockStatus | `` | Defines the lock status of a DMFile (file in a Library, Cell or View). Members: NOT_LOCKED : 'NotLocked': The file is not locked. LOCKED_BY_CURRENT_PROCESS : 'LockedByCurrentProcess': The file is locked by the current... |
| `keysight.ads.de.DMLockStatus.LOCKED_BY_FOREIGN_PROCESS` | DMLockStatus | `` | Defines the lock status of a DMFile (file in a Library, Cell or View). Members: NOT_LOCKED : 'NotLocked': The file is not locked. LOCKED_BY_CURRENT_PROCESS : 'LockedByCurrentProcess': The file is locked by the current... |
| `keysight.ads.de.DMLockStatus.NOT_LOCKED` | DMLockStatus | `` | Defines the lock status of a DMFile (file in a Library, Cell or View). Members: NOT_LOCKED : 'NotLocked': The file is not locked. LOCKED_BY_CURRENT_PROCESS : 'LockedByCurrentProcess': The file is locked by the current... |
| `keysight.ads.de.find_equivalent_design` | function | `(design: 'Design') -> Optional[ForwardRef('Design')]` | Return the equivalent design. If design is the 'schematic' view, return the 'layout' view. If design is the 'layout' view, return the 'schematic' view. |
| `keysight.ads.de.find_inst_in_associated_schematic` | function | `(inst_name: str, design: 'Design') -> tuple['Instance', 'Design']` | Find the named instance in the associated schematic of the given design. Typically used to find the substrate or process block referenced by parameters of layout instances. The value returned is a tuple containing the... |
| `keysight.ads.de.find_inst_in_schematic_hierarchy` | function | `(inst_name: str, hierarchy: 'DesignHierarchy') -> tuple['Instance', 'Design']` | Search up the hierarchy to find the named instance in the associated schematics of the designs in the hierarchy. Typically used to find the substrate or process block referenced by parameters of layout instances. The ... |
| `keysight.ads.de.GenPolygon.empty` | property | `` |  |
| `keysight.ads.de.GenPolygon.remove_arcs` | function | `(self, arc_resolution_degrees: float) -> None` |  |
| `keysight.ads.de.GenPolygonWithHoles.empty` | property | `` |  |
| `keysight.ads.de.GenPolygonWithHoles.remove_arcs` | function | `(self, arc_resolution_degrees: float) -> None` |  |
| `keysight.ads.de.GenPolyline.empty` | property | `` |  |
| `keysight.ads.de.GenPolyline.teardrop_info` | property | `` | teardrop_info is deprecated, and will be removed in the 2027 release. Use teardrops or teardrop_touches. |
| `keysight.ads.de.get_cell_module` | function | `(lib_name: str, cell_name: str) -> module` | Import the Python module for an OpenAccess cell. |
| `keysight.ads.de.get_library_module` | function | `(lib_name: str) -> module` | Import the Python module for an OpenAccess library. |
| `keysight.ads.de.get_path_for_use_in_library_definition_file` | function | `(path: pathlib._local.Path \| str, lib_def_file_path: pathlib._local.Path \| str) -> str` | Convert a path to a simplified path for use in a library definition file. The simplified path may be relative to the library definition file path or may contain environment variable references of the form $VAR/path. |
| `keysight.ads.de.get_smart_package_module` | function | `(package_name: str) -> module` | Import the Python module for an ADS Smart Package. |
| `keysight.ads.de.get_view_module` | function | `(lib_name: str, cell_name: str, view_name: str) -> module` | Import the Python module for an OpenAccess cellview. |
| `keysight.ads.de.ItemEditMode` | class | `` | Members: DIALOG NEW ON_SCREEN TEMP |
| `keysight.ads.de.ItemEditMode.DIALOG` | ItemEditMode | `` | Members: DIALOG NEW ON_SCREEN TEMP |
| `keysight.ads.de.ItemEditMode.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.ItemEditMode.NEW` | ItemEditMode | `` | Members: DIALOG NEW ON_SCREEN TEMP |
| `keysight.ads.de.ItemEditMode.ON_SCREEN` | ItemEditMode | `` | Members: DIALOG NEW ON_SCREEN TEMP |
| `keysight.ads.de.ItemEditMode.TEMP` | ItemEditMode | `` | Members: DIALOG NEW ON_SCREEN TEMP |
| `keysight.ads.de.ItemEditMode.value` | property | `` |  |
| `keysight.ads.de.ItemInfo` | class | `(design: 'TDesign', master: 'CellviewRefLike', edit_mode: keysight.ads.de._pde.ItemEditMode) -> None` |  |
| `keysight.ads.de.ItemInfo.cell_name` | property | `` |  |
| `keysight.ads.de.ItemInfo.create_new_instance` | function | `(self, location: keysight.ads.de._points.PointF \| tuple[float, float], auto_connect: bool = False) -> 'Instance'` |  |
| `keysight.ads.de.ItemInfo.design_name` | property | `` |  |
| `keysight.ads.de.ItemInfo.display_name` | property | `` |  |
| `keysight.ads.de.ItemInfo.inst_name` | property | `` |  |
| `keysight.ads.de.ItemInfo.instance` | property | `` |  |
| `keysight.ads.de.ItemInfo.is_scope_global` | property | `` |  |
| `keysight.ads.de.ItemInfo.is_scope_nested` | property | `` |  |
| `keysight.ads.de.ItemInfo.lib_name` | property | `` |  |
| `keysight.ads.de.ItemInfo.model_def` | property | `` |  |
| `keysight.ads.de.ItemInfo.owner_design` | property | `` |  |
| `keysight.ads.de.ItemInfo.parameters` | property | `` | Parameters stored on the ItemInfo. These may be temporary values set during editing or from parameter callbacks. |
| `keysight.ads.de.ItemInfo.set_scope_global` | function | `(self) -> None` |  |
| `keysight.ads.de.ItemInfo.set_scope_nested` | function | `(self) -> None` |  |
| `keysight.ads.de.ItemInfo.setup_instance_for_edit` | function | `(self, instance: 'Instance', mod_inst_name_pref: bool = False) -> None` |  |
| `keysight.ads.de.ItemInfo.view_name` | property | `` |  |
| `keysight.ads.de.Layer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for Layer objects in Tech. Layer objects become invalid when the technology is modified. So the Python objects should have a short lifetime. |
| `keysight.ads.de.Layer.abbreviation` | property | `` |  |
| `keysight.ads.de.Layer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.Layer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.Layer.layer_binding` | property | `` |  |
| `keysight.ads.de.Layer.library` | property | `` |  |
| `keysight.ads.de.Layer.name` | property | `` |  |
| `keysight.ads.de.Layer.number` | property | `` |  |
| `keysight.ads.de.Layer.process_role` | property | `` |  |
| `keysight.ads.de.Layer.tech` | property | `` |  |
| `keysight.ads.de.LayerSlice` | class | `(library: Optional[keysight.ads.de._core.library.Library] = None, layer: Union[str, keysight.ads.de.db._layer_id.LayerId, NoneType] = None, enclosure_width_uu: Optional[float] = None) -> None` | Represents a single slice of a LineStrip. Identifies the layer for this slice and its enclosure. |
| `keysight.ads.de.LayerSlice.create_from_layer_id` | method | `(library: keysight.ads.de._core.library.Library, layer_id: keysight.ads.de.db._layer_id.LayerId, enclosure_width: float) -> 'LayerSlice'` |  |
| `keysight.ads.de.LayerSlice.create_from_names` | method | `(library: keysight.ads.de._core.library.Library, layer_name: str, purpose_name: str, enclosure_width: float) -> 'LayerSlice'` |  |
| `keysight.ads.de.LayerSlice.enclosure_width_uu` | property | `` | Return the difference in width (in user units) between this slice and the default width of the strip. |
| `keysight.ads.de.LayerSlice.layer_id` | property | `` |  |
| `keysight.ads.de.LayerSlice.layer_name` | property | `` |  |
| `keysight.ads.de.LayerSlice.purpose_name` | property | `` |  |
| `keysight.ads.de.LayerSlice.validate_names_and_id` | function | `(self, library: keysight.ads.de._core.library.Library) -> None` | Check that the layer_id matches the layer and purpose names. |
| `keysight.ads.de.LCVName.is_empty` | property | `` |  |
| `keysight.ads.de.LibDefList` | class | `()` | Represents a library definition file. The current implementation supports only short term usage. The members are a snapshot of the members at the time the LibDefList was created. |
| `keysight.ads.de.LibDefList.members` | property | `` | The members of this library definition file. |
| `keysight.ads.de.LibDefListMem` | class | `()` | Represents a member of a LibDefList - either a library or include. |
| `keysight.ads.de.LibDefListMem.is_library` | property | `` | True if this is a library. |
| `keysight.ads.de.Library` | class | `()` | Base class for Library, Cell, and View. Library, Cell and View are part of the Data Management System and are containers for files (known as DMFiles). Each instance represents not only the library, cell or view, but a... |
| `keysight.ads.de.Library.get_layout_preference` | function | `(self, index: 'LibSpecificPreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.get_library_cfg_var` | function | `(self, pref_name: str) -> str` | Get a variable from the library configuration file. If the value contains environment variable references, those values will be substituted. |
| `keysight.ads.de.Library.get_schematic_preference` | function | `(self, index: 'LibSpecificPreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.physical_layer_names` | property | `` |  |
| `keysight.ads.de.Library.set_layout_preference` | function | `(self, index: 'LibSpecificPreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.set_schematic_preference` | function | `(self, index: 'LibSpecificPreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.setup_schematic_tech` | function | `(self, interoperable: bool = False) -> None` |  |
| `keysight.ads.de.LibraryMode` | class | `` | Specifies the mode to use when opening a library. Members: UNKNOWN : 'Unknown': No mode specified. SHARED : 'Shared': Open the library for read-write allowing access from other processes. NON_SHARED : 'NonShared': Ope... |
| `keysight.ads.de.LibraryMode.NON_SHARED` | LibraryMode | `` | Specifies the mode to use when opening a library. Members: UNKNOWN : 'Unknown': No mode specified. SHARED : 'Shared': Open the library for read-write allowing access from other processes. NON_SHARED : 'NonShared': Ope... |
| `keysight.ads.de.LibraryMode.READ_ONLY` | LibraryMode | `` | Specifies the mode to use when opening a library. Members: UNKNOWN : 'Unknown': No mode specified. SHARED : 'Shared': Open the library for read-write allowing access from other processes. NON_SHARED : 'NonShared': Ope... |
| `keysight.ads.de.LibraryMode.SHARED` | LibraryMode | `` | Specifies the mode to use when opening a library. Members: UNKNOWN : 'Unknown': No mode specified. SHARED : 'Shared': Open the library for read-write allowing access from other processes. NON_SHARED : 'NonShared': Ope... |
| `keysight.ads.de.LibraryMode.UNKNOWN` | LibraryMode | `` | Specifies the mode to use when opening a library. Members: UNKNOWN : 'Unknown': No mode specified. SHARED : 'Shared': Open the library for read-write allowing access from other processes. NON_SHARED : 'NonShared': Ope... |
| `keysight.ads.de.LineBeginEndTypes` | class | `(*args, **kwargs)` | Deprecated. Use LineEndType instead. LineBeginEndTypes is deprecated, and will be removed in the 2027 release. Use LineEndType |
| `keysight.ads.de.LineBeginEndTypes.CHAMFER` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.CHAMFERED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.EXTEND` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.EXTENDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.ROUND` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.ROUNDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.TRUNCATE` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineBeginEndTypes.TRUNCATED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.LineClearance.layer_name` | property | `` |  |
| `keysight.ads.de.LineCornerTypes` | class | `(*args, **kwargs)` | Deprecated. Use LineCornerType instead. LineCornerTypes is deprecated, and will be removed in the 2027 release. Use LineCornerType |
| `keysight.ads.de.LineCornerTypes.ADAPTIVE_MITER_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.ADAPTIVE_MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.CURVE_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.CURVED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.MITERED_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.ROUND` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.ROUND_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.SQUARE` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineCornerTypes.SQUARE_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.LineItem` | class | `(name: Optional[str] = None) -> None` | Defines transmission line types. A LineItem must be saved in a library in order to be used by layout designs. |
| `keysight.ads.de.LineItem.add_clearance` | function | `(self, clearance: keysight.ads.de.tech._tech.LineClearance) -> None` |  |
| `keysight.ads.de.LineItem.begin_end_type` | property | `` | The type of ending (and beginning) of lines defined by this line item. |
| `keysight.ads.de.LineItem.clearances` | property | `` | The collection of line clearances in this LineItem. |
| `keysight.ads.de.LineItem.corner` | property | `` | Defines the corners (bends) of lines defined by this line item. |
| `keysight.ads.de.LineItem.description` | property | `` | Description of this line type definition used by tooltips. |
| `keysight.ads.de.LineItem.get_calculated_type_deprecated` | function | `(self) -> str` |  |
| `keysight.ads.de.LineItem.is_single_strip_line` | property | `` |  |
| `keysight.ads.de.LineItem.name` | property | `` | Name of this line type definition. References to line items by layout objects use this name. |
| `keysight.ads.de.LineItem.plane_layer_names` | property | `` | The collection of plane layer names used by this line item. |
| `keysight.ads.de.LineItem.simulation_model` | property | `` |  |
| `keysight.ads.de.LineItem.single_strip_line` | property | `` | The only strip item if this line is single-strip. Will raise an exception if this line is not single-strip. |
| `keysight.ads.de.LineItem.strip_items` | property | `` | The collection of line strips in this LineItem. |
| `keysight.ads.de.LineItem.substrate` | property | `` | Name of the substrate used by this Line type definition. |
| `keysight.ads.de.LineItem.type` | property | `` | Legacy type - not really used now. |
| `keysight.ads.de.LineItem.uses_layer_id` | function | `(self, layer_id: keysight.ads.de.db._layer_id.LayerId) -> bool` |  |
| `keysight.ads.de.LineStripItem` | class | `(library: Optional[keysight.ads.de._core.library.Library] = None, layer_name: Optional[str] = None, purpose_name: Optional[str] = None, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None) -> None` | Represents a single strip of a line type. |
| `keysight.ads.de.LineStripItem.add_layer_slice` | function | `(self, library: keysight.ads.de._core.library.Library, layer_name: str, purpose_name: str, width: float = 0.0) -> None` | Create a LayerSlice and append it to layer_slices. |
| `keysight.ads.de.LineStripItem.default_width` | property | `` | The default width (in user units) of the layer slices. |
| `keysight.ads.de.LineStripItem.has_multiple_slices` | property | `` |  |
| `keysight.ads.de.LineStripItem.layer_slices` | property | `` | Return the collection of layer slices in this LineStripItem. |
| `keysight.ads.de.LineStripItem.strip_id` | property | `` |  |
| `keysight.ads.de.LineStripItem.strip_spacing_type` | property | `` | Returns the type of spacing required between this strip and the next strip. |
| `keysight.ads.de.LineStripItem.strip_spacing_value` | property | `` | Returns the spacing required between this strip and the next strip. |
| `keysight.ads.de.LineStripItem.uses_layer_id` | function | `(self, layer_id: keysight.ads.de.db._layer_id.LayerId) -> bool` | Return True if any LayerSlice is on the given layer. |
| `keysight.ads.de.LineStripSpacingTypes` | class | `(*args, **kwargs)` | LineStripSpacingTypes is deprecated, and will be removed in the 2027 release. Use LineStripSpacingType |
| `keysight.ads.de.LineStripSpacingTypes.CENTER_LINE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.LineStripSpacingTypes.EDGE_TO_EDGE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.LineStripSpacingTypes.NO_SPACING` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.LineTypeSimulationModel.use_single_tline_element_to_model_a_trace` | property | `` |  |
| `keysight.ads.de.Namespace.from_file_system` | function | `(self, name: str, ns: 'NS \| str \| Library' = <NS.WIN: 1>) -> str` | Convert a name in the file system namespace to a name in this namespace. |
| `keysight.ads.de.Namespace.is_valid_name` | function | `(self, name: str) -> bool` | Determine if name is valid in this namespace. |
| `keysight.ads.de.Namespace.to_file_system` | function | `(self, name: str, ns: 'NS \| str \| Library' = <NS.WIN: 1>) -> str` | Convert a name in this namespace to a name in the file system namespace. |
| `keysight.ads.de.NS` | class | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.NS.CDBA` | NS | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.NS.NATIVE` | NS | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.NS.NETLIST` | NS | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.NS.UNIX` | NS | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.NS.WIN` | NS | `` | Specifies the type of Namespace used for a category of names. Members: NATIVE : 'Native': The flexible, case-sensitive, generic namespace. Used for Cell and View names. WIN : 'Win': Used for file names in libraries cr... |
| `keysight.ads.de.OAMaterial` | class | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.CONTACTLESS_METAL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.CUT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.METAL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.N_DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.N_IMPLANT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.N_WELL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.OTHER` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.P_DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.P_IMPLANT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.P_WELL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.PASSIVATION_CUT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.POLY` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.OAMaterial.RECOGNITION` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.Outline.edges` | property | `` | The collection of edges for this outline. The edges are only for short term use. |
| `keysight.ads.de.Outline.empty` | property | `` | True if the outline has no points. |
| `keysight.ads.de.Outline.remove_arcs` | function | `(self, arc_resolution_degrees: float) -> None` |  |
| `keysight.ads.de.PaperSize` | class | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A0` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A1` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A2` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A3` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A4` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A5` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A6` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A7` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A8` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.A9` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B0` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B1` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B10` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B2` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B3` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B4` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B5` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B6` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B7` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B8` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.B9` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.C5E` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.COMM10E` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.DLE` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.EXECUTIVE` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.FOLIO` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.LEDGER` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.LEGAL` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.LETTER` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PaperSize.TABLOID` | PaperSize | `` | Members: A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 C5E COMM10E DLE EXECUTIVE FOLIO LEDGER LEGAL LETTER TABLOID |
| `keysight.ads.de.PhysicalLayer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a physical layer (one that contains shapes and figures). |
| `keysight.ads.de.PhysicalLayer.abbreviation` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.create` | function | `(tech: 'Tech', layer_name: str, layer_num: int) -> 'PhysicalLayer'` |  |
| `keysight.ads.de.PhysicalLayer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.PhysicalLayer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.PhysicalLayer.layer_binding` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.library` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.mask_number` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.material` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.mfg_grid` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.name` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.number` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.process_role` | property | `` |  |
| `keysight.ads.de.PhysicalLayer.tech` | property | `` |  |
| `keysight.ads.de.PrinterColorMode` | class | `` | Members: COLOR GRAYSCALE |
| `keysight.ads.de.PrinterColorMode.COLOR` | PrinterColorMode | `` | Members: COLOR GRAYSCALE |
| `keysight.ads.de.PrinterColorMode.GRAYSCALE` | PrinterColorMode | `` | Members: COLOR GRAYSCALE |
| `keysight.ads.de.PrinterOrientation` | class | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.PrinterOrientation.LANDSCAPE` | PrinterOrientation | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.PrinterOrientation.PORTRAIT` | PrinterOrientation | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.ProcessRole` | class | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.ANNOT_COMPONENT_NAME` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.ANNOT_INSTANCE_NAME` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.ANNOT_OTHER` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.BOUNDARY` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.COMPONENT_BODY` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.CONDUCTOR` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.CONDUCTOR_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.CONDUCTOR_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.DIELECTRIC` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.DIELECTRIC_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.DIELECTRIC_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.DRC` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.HEAT_SOURCE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.NONE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.NOT_DEFINED` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.OTHER` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SCRATCH` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SEMICONDUCTOR` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SEMICONDUCTOR_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SEMICONDUCTOR_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SILK_SCREEN` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SOLDER_MASK` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.ProcessRole.SOLDER_PASTE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.remove_smart_package` | function | `(package_name: str) -> None` | Remove the named ADS Smart Package. |
| `keysight.ads.de.TeardropLineInfo.definition` | function | `(self, end: keysight.ads.de._pde.TeardropLineInfo.End \| str) -> keysight.ads.de.db._teardrop.TeardropDefinition` | definition is deprecated, and will be removed in the 2027 release. Use GenPolyline.teardrops. |
| `keysight.ads.de.TeardropLineInfo.has_teardrops` | property | `` | True if either end actually has teardrop touches. has_teardrops is deprecated, and will be removed in the 2027 release. Use GenPolyline.teardrop_touches. |
| `keysight.ads.de.TeardropLineInfo.set_definition` | function | `(self, definition: keysight.ads.de.db._teardrop.TeardropDefinition, end: keysight.ads.de._pde.TeardropLineInfo.End \| str) -> None` | set_definition is deprecated, and will be removed in the 2027 release. Use GenPolyline.teardrops. |
| `keysight.ads.de.TeardropLineInfo.set_touching` | function | `(self, touching: keysight.ads.de.db._teardrop.TeardropTouching, end: keysight.ads.de._pde.TeardropLineInfo.End \| str) -> None` | set_touching is deprecated, and will be removed in the 2027 release. Use GenPolyline.teardrop_touches. |
| `keysight.ads.de.TeardropLineInfo.touch` | function | `(self, end: keysight.ads.de._pde.TeardropLineInfo.End \| str) -> keysight.ads.de.db._teardrop.TeardropTouching` | touch is deprecated, and will be removed in the 2027 release. Use GenPolyline.teardrop_touches. |
| `keysight.ads.de.Tech` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a technology database for a library. This Tech can reference (i.e. inherit) the technology from other libraries. |
| `keysight.ads.de.Tech.actual_interop_type` | property | `` | The effective interoperability type determined by settings in this tech and inherited tech. |
| `keysight.ads.de.Tech.all_layers` | property | `` | Return the complete collection of layers in this Tech database. The collection also includes Layers from referenced technology. |
| `keysight.ads.de.Tech.all_purposes` | property | `` | Return the complete collection of Purposes in this Tech database. The collection also includes Purposes from referenced technology. |
| `keysight.ads.de.Tech.create_derived_layer_boolean` | function | `(self, layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, layer2: keysight.ads.de.tech._tech.Layer \| str) -> keysight.ads.de.tech._tech.DerivedLayer` | Create a derived layer from two source layers and boolean operation. The derived layer contains all the shapes that result by performing the boolean operation on all the shapes from the two source layers. |
| `keysight.ads.de.Tech.create_derived_layer_sizing` | function | `(self, layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, distance: int) -> keysight.ads.de.tech._tech.DerivedLayer` | Create a derived layer from a single source layer, a sizing operation, and a distance parameter. The derived layer contains all the shapes that result by performing the sizing operation on all the shapes from the sour... |
| `keysight.ads.de.Tech.create_physical_layer` | function | `(self, layer_name: str, layer_num: int) -> keysight.ads.de.tech._tech.PhysicalLayer` |  |
| `keysight.ads.de.Tech.dbu_per_uu_sch` | property | `` | The ratio of database units to user units in schematic and symbol views. |
| `keysight.ads.de.Tech.delete_all_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.Tech.delete_layer` | function | `(self, layer: Union[str, int, keysight.ads.de.tech._tech.Layer]) -> None` |  |
| `keysight.ads.de.Tech.find_layer` | function | `(self, layer: Union[int, str], local: bool = False) -> Optional[keysight.ads.de.tech._tech.Layer]` |  |
| `keysight.ads.de.Tech.interop_type` | property | `` | The interoperability type defined in this tech only. If this technology does not have resolution defined, this will be InteropType.UNSPECIFIED. To get the interoperability type determined by inherited tech, use actual... |
| `keysight.ads.de.Tech.layer` | function | `(self, layer: Union[int, str], local: bool = False) -> keysight.ads.de.tech._tech.Layer` |  |
| `keysight.ads.de.Tech.layer_maps` | property | `` | Return the collection of layer maps in this Tech database. |
| `keysight.ads.de.Tech.layer_names` | function | `(self, local: bool = False) -> list[str]` | Get the names of all the physical layers. |
| `keysight.ads.de.Tech.layer_numbers` | function | `(self, local: bool = False) -> list[int]` | Get the numbers of all the physical layers. |
| `keysight.ads.de.Tech.layers` | property | `` | Return the collection of layers in this Tech database. The collection only includes Layers defined in this tech. |
| `keysight.ads.de.Tech.referenced_lib_names` | property | `` | The names of the libraries directly referenced by this Tech. |
| `keysight.ads.de.Tech.save_layer_maps` | function | `(self) -> None` | Save the layer maps to this Tech's library. |
| `keysight.ads.de.Tech.user_units_sch` | property | `` | The name of the user units used in schematic and symbol views. |
| `keysight.ads.de.TouchType` | class | `` | Members: NONE CIRCLE |
| `keysight.ads.de.TouchType.CIRCLE` | TouchType | `` | Members: NONE CIRCLE |
| `keysight.ads.de.TouchType.NONE` | TouchType | `` | Members: NONE CIRCLE |
| `keysight.ads.de.unarchive_file` | function | `(zap_file_path: str \| pathlib._local.Path \| os.PathLike, dest_path: str \| pathlib._local.Path \| os.PathLike, *, exclude_em_files: bool = False) -> None` | Unarchive a workspace 7zads file. Usage: de.unarchive_file(zap_name, dest_path) de.unarchive_file(zap_name, dest_path, exclude_em_files=True) |
| `keysight.ads.de.update_ael_wrapping_types` | function | `() -> None` |  |
| `keysight.ads.de.View` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for Library, Cell, and View. Library, Cell and View are part of the Data Management System and are containers for files (known as DMFiles). Each instance represents not only the library, cell or view, but a... |
| `keysight.ads.de.View.is_schematic_view` | property | `` |  |
| `keysight.ads.de.Workspace.get_layout_preference` | function | `(self, index: 'WorkspacePreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.get_schematic_preference` | function | `(self, index: 'WorkspacePreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.remove_library` | function | `(self, library_name: str, library_path: pathlib._local.Path \| str) -> None` |  |
| `keysight.ads.de.Workspace.remove_library_definition_file` | function | `(self, lib_def_file_path: pathlib._local.Path \| str) -> None` |  |
| `keysight.ads.de.Workspace.set_layout_preference` | function | `(self, index: 'WorkspacePreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.set_schematic_preference` | function | `(self, index: 'WorkspacePreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |

### `keysight.ads.de.db_uu`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.db_uu.AnnotData.comp_name_layer` | property | `` | The layer used for component name annotation. |
| `keysight.ads.de.db_uu.AnnotData.inst_name_layer` | property | `` | The layer used for instance name annotation. |
| `keysight.ads.de.db_uu.AnnotData.param_layer` | property | `` | The layer used for parameter annotation. |
| `keysight.ads.de.db_uu.ApolloObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ApolloObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AppObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.AppObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Arc.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Arc.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Arc.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Arc.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Arc.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Arc.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Arc.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ArrayInst.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.ArrayInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ArrayInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ArrayInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.ArrayInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.ArrayInst.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.ArrayInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.ArrayInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.ArrayInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.ArrayInst.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.ArrayInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.ArrayInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.ArrayInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.ArrayInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.pin` | property | `` |  |
| `keysight.ads.de.db_uu.ArrayInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.ArrayInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ArrayInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.AttrDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.AttrDisplay.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.AttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.AttrDisplay.layer` | property | `` |  |
| `keysight.ads.de.db_uu.AttrDisplay.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.AttrDisplay.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.AttrDisplay.pin` | property | `` |  |
| `keysight.ads.de.db_uu.AttrDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.BlockObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BlockObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BundleNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleNet.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.BundleNet.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.BundleNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name contains commas separating the bits (e.g. "a, b, c"). |
| `keysight.ads.de.db_uu.BundleTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BundleTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BundleTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BundleTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BundleTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BundleTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BundleTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BundleTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BundleTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BundleTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BundleTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BundleTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BundleTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BundleTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BundleTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BundleTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BundleTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.BusNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusNet.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.BusNet.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.BusNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BusNetBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusNetBit.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNetBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusNetBit.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.BusNetBit.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.BusNetBit.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusNetBit.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, base_name: str, start: int, stop: int, step: int = 1, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name uses bus syntax (e.g. "P<0:7>"). |
| `keysight.ads.de.db_uu.BusTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BusTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BusTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BusTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BusTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BusTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BusTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BusTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BusTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BusTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BusTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.BusTermBit` | class | `(net: keysight.ads.de.db_uu._db_x.Net, base_name: str, bit: int, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A multi-bit term whose name uses bus syntax (e.g. "P<0:7>"). |
| `keysight.ads.de.db_uu.BusTermBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.BusTermBit.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTermBit.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.BusTermBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTermBit.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.BusTermBit.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.BusTermBit.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTermBit.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.BusTermBit.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.BusTermBit.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.BusTermBit.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.BusTermBit.name` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.net` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.BusTermBit.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.BusTermBit.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.BusTermBit.props` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.BusTermBit.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusTermBit.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.BusTermBit.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.CompositeObject.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.CompositeObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CompositeObject.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.CompositeObject.members` | property | `` |  |
| `keysight.ads.de.db_uu.CompoundForm` | class | `(name: str, label: str = '', params: collections.abc.Sequence[keysight.ads.de.db._model_def.ModelParam] = [], net_format: str = '', display_format: str = '', dialog_data: str = '') -> None` | CompoundForm is a type of Form for a parameter that contains one or more sub-parameters. The CompoundForm describes how the parameter is netlisted and displayed. The Form for each sub-parameter describes how that port... |
| `keysight.ads.de.db_uu.CompoundForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ConnectivityOptions.calculate_flight_lines_between_grounds` | property | `` | True if flight lines are calculated between ground nets. |
| `keysight.ads.de.db_uu.ConstForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ConstructionLine.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ConstructionLine.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ConstructionLine.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.create_schematic` | function | `(name: 'CellviewRefLike') -> keysight.ads.de.db_uu._design.Design` | Create a schematic from an open library in the active workspace. Parameters ---------- name: CellviewRefLike The name of the design, usually of the form "LibraryName:CellName:schematic" Example ------- >>> design = de... |
| `keysight.ads.de.db_uu.CustomVia` | class | `(design: 'Design', via_def_name: str, origin: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> None` | A custom OpenAccess Via. The via is defined partly by its definition in the technology. The geometry of a custom via is determined by another design. |
| `keysight.ads.de.db_uu.CustomVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.CustomVia.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.CustomVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CustomVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.CustomVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.CustomVia.pin` | property | `` |  |
| `keysight.ads.de.db_uu.CustomVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.CustomVia.via_master_lcv_name` | property | `` | The cellview name of the master design referenced by this custom via. |
| `keysight.ads.de.db_uu.Design.add_dot_for_pin` | function | `(self, loc: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> 'Dot'` |  |
| `keysight.ads.de.db_uu.Design.add_numbered_term` | function | `(self, net: 'Net', term_name: str, term_number: int, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>) -> 'Term'` | Add a numbered term to the design. This new Term will connect by number. If any Term in the design connects by number, then all Terms in the design need to connect by number. |
| `keysight.ads.de.db_uu.Design.add_pad_with_drill_layer` | function | `(self, padstack: 'Padstack \| str', drill_layer: 'LayerId \| int', loc: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None) -> 'PCBPad'` |  |
| `keysight.ads.de.db_uu.Design.add_pad_with_specified_layers` | function | `(self, padstack: 'Padstack \| str', top_layer: 'LayerId \| int', bottom_layer: 'LayerId \| int', loc: Union[keysight.ads.de._points.PointF, tuple[float, float]], minimize_drills: bool = True, *, name: Optional[str] = None, angle: Optional[float] = None) -> 'PCBPad'` |  |
| `keysight.ads.de.db_uu.Design.add_pin` | function | `(self, *args, **kwargs) -> 'Pin'` |  |
| `keysight.ads.de.db_uu.Design.add_pin_fig_for_term_type` | function | `(self, term_type: keysight.ads.de._pde.db.TermType \| str, loc: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> 'PinFig'` |  |
| `keysight.ads.de.db_uu.Design.add_power_term` | function | `(self, term_name: str, power: str, default_net: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Design.add_single_layer_pad` | function | `(self, padstack: 'Padstack \| str', pad_layer: 'LayerId \| int', loc: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None) -> 'PCBPad'` |  |
| `keysight.ads.de.db_uu.Design.add_term` | function | `(self, net: 'Net', term_name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>) -> 'Term'` | Add a term to the design. This new Term will connect by name. If any Term in the design connects by name, then all Terms in the design need to connect by name. |
| `keysight.ads.de.db_uu.Design.add_via_with_drill_layer` | function | `(self, padstack: 'Padstack \| str', drill_layer: 'LayerId \| int', loc: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None) -> 'PCBVia'` |  |
| `keysight.ads.de.db_uu.Design.add_via_with_specified_layers` | function | `(self, padstack: 'Padstack \| str', top_layer: 'LayerId \| int', bottom_layer: 'LayerId \| int', loc: Union[keysight.ads.de._points.PointF, tuple[float, float]], minimize_drills: bool = True, *, name: Optional[str] = None, angle: Optional[float] = None) -> 'PCBVia'` |  |
| `keysight.ads.de.db_uu.Design.config_view_name` | property | `` | The config view name for this design. Will be empty if there is no simulation setting for config view. |
| `keysight.ads.de.db_uu.Design.create_layer_id` | function | `(self, layer_name: str, purpose_name: Optional[str] = None) -> 'LayerId'` | Return the LayerId for the given layer name and purpose name. |
| `keysight.ads.de.db_uu.Design.default_wire_layer` | property | `` | The default wire layer for wires. This is intended for schematics and typically returns LayerId(228). |
| `keysight.ads.de.db_uu.Design.find_term` | function | `(self, term_name: str) -> Optional[ForwardRef('Term')]` |  |
| `keysight.ads.de.db_uu.Design.find_term_numbered` | function | `(self, term_number: int) -> Optional[ForwardRef('Term')]` |  |
| `keysight.ads.de.db_uu.Design.get_layer_for_pin` | function | `(self) -> 'LayerId'` |  |
| `keysight.ads.de.db_uu.Design.get_layers` | function | `(self) -> list['LayerId']` |  |
| `keysight.ads.de.db_uu.Design.get_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')]) -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Design.get_snap_angle_for_new_pin` | function | `(self, loc: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> float` |  |
| `keysight.ads.de.db_uu.Design.get_snap_layer_for_new_pin` | function | `(self, loc: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> 'LayerId'` |  |
| `keysight.ads.de.db_uu.Design.get_term_iter` | function | `(self) -> 'TermIter'` |  |
| `keysight.ads.de.db_uu.Design.is_schematic` | property | `` |  |
| `keysight.ads.de.db_uu.Design.move_selected` | function | `(self, offset: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, disconnect: bool = False, adjust_edges: bool = False, route_trace: bool = False) -> None` | Move the selected objects by the given offset. If disconnect is True, wires and traces will be disconnected from pins and instance pins. If adjust_edges is True and vertices are selected, edges will be adjusted to mai... |
| `keysight.ads.de.db_uu.Design.set_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')], value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Design.terms` | property | `` |  |
| `keysight.ads.de.db_uu.DesignAttrType` | class | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.CELL_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.CELL_TYPE` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.LAST_SAVED_TIME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.LIB_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignAttrType.VIEW_NAME` | DesignAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME CELL_TYPE LAST_SAVED_TIME |
| `keysight.ads.de.db_uu.DesignMode` | class | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.APPEND` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.READ_ONLY` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.DesignMode.WRITE` | DesignMode | `` | Specifies the mode for opening a design. Members: READ_ONLY : 'ReadOnly': Open the design for reading. WRITE : 'Write': Open the design for writing and delete its contents. APPEND : 'Append': Open the design for editing. |
| `keysight.ads.de.db_uu.Donut.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Donut.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Donut.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Donut.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Donut.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Donut.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Donut.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Donut.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Donut.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Dot.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Dot.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Dot.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Dot.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Dot.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Dot.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Dot.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Dot.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Dot.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Ellipse.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Ellipse.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Ellipse.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ellipse.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ellipse.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Ellipse.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Ellipse.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Ellipse.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Ellipse.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Boundary Walls for momentum simulation. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.box` | property | `` | A copy of the boundary wall's box. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_box` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a box boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_fem_symmetry` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a FEM symmetry boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_partial_waveguide` | function | `(design: keysight.ads.de.db_uu._design.Design, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create an incomplete waveguide boundary wall. This should not be used except when trying to recreate an incomplete waveguide. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.create_waveguide` | function | `(design: keysight.ads.de.db_uu._design.Design, horizontal: bool, box: keysight.ads.de._points.BoxF) -> 'EMBoundaryWalls'` | Create a waveguide boundary wall. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_box` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_fem_symmetry` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_horizontal_waveguide` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_partial_waveguide` | property | `` | True if this is a waveguide that is incomplete. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.is_vertical_waveguide` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.move` | function | `(self, offset: Union[keysight.ads.de._points.PointF, tuple[float, float]]) -> None` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.props` | property | `` |  |
| `keysight.ads.de.db_uu.EMBoundaryWalls.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.EvalText` | class | `(design: keysight.ads.de.db_uu._design.Design, layer_id: keysight.ads.de.db._layer_id.LayerId, expression: str, evaluator: str, origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], font_name: str, height: float, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.CENTER_LEFT: 1>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>, has_overbar: bool = False, is_visible: bool = True, is_drafting: bool = True) -> None` | Custom text with an evaluator that determines what text gets displayed. |
| `keysight.ads.de.db_uu.EvalText.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.EvalText.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.EvalText.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EvalText.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.EvalText.layer` | property | `` |  |
| `keysight.ads.de.db_uu.EvalText.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.EvalText.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.EvalText.pin` | property | `` |  |
| `keysight.ads.de.db_uu.EvalText.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ExpressionContext.setup_hierarchy_for_design` | function | `(self, design: 'DesignDbu \| DesignUu') -> None` |  |
| `keysight.ads.de.db_uu.ExpressionContext.setup_hierarchy_for_layout_only` | function | `(self, design: 'DesignDbu \| DesignUu') -> None` |  |
| `keysight.ads.de.db_uu.Fig.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Fig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Fig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroup` | class | `(design: 'Design', name: str) -> None` | A collection of figures that can be reused. This collection is called a Group in the ADS UI. A Pin is considered to be a member of a FigGroup if all of its PinFigs are members. A composite object is considered to be a... |
| `keysight.ads.de.db_uu.FigGroup.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.FigGroup.add_objects` | function | `(self, objects: collections.abc.Sequence[keysight.ads.de.db_uu._db_x.ApolloObject]) -> None` | Add the objects to this FigGroup if not already a member. |
| `keysight.ads.de.db_uu.FigGroup.add_to_fig_group` | function | `(self, obj: keysight.ads.de.db_uu._db_x.ApolloObject) -> None` | Add obj to this FigGroup. If obj is a pin, all of its PinFigs will be added. If obj is a composite object, all of its Figs will be added. |
| `keysight.ads.de.db_uu.FigGroup.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.FigGroup.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroup.members` | property | `` |  |
| `keysight.ads.de.db_uu.FigGroup.remove_from_fig_group` | function | `(self, obj: keysight.ads.de.db_uu._db_x.ApolloObject) -> None` | Remove obj from this FigGroup. If obj is a pin, all of its PinFigs will be removed. If obj is a composite object, all of its Figs will be removed. |
| `keysight.ads.de.db_uu.FigGroupMem` | class | `(fig_group: 'FigGroup', fig: 'Fig') -> None` | A link between a FigGroup and a member object (Fig). |
| `keysight.ads.de.db_uu.FigGroupMem.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.FigGroupMem.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.FigGroupMem.fig` | property | `` | The Fig represented by this member. |
| `keysight.ads.de.db_uu.FigGroupMem.fig_group` | property | `` | The FigGroup that contains this member. |
| `keysight.ads.de.db_uu.FigGroupMem.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.FigGroupMem.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.FigGroupMem.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.FigGroupMem.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.FigGroupMem.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.FigGroupMem.props` | property | `` |  |
| `keysight.ads.de.db_uu.FigGroupMem.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.Form.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.Group.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Group.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Group.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Group.members` | property | `` |  |
| `keysight.ads.de.db_uu.GroupMember` | class | `(group: keysight.ads.de.db_uu._db_x.Group, obj: keysight.ads.de.db_uu._db_x.ApolloObject, is_leader: bool = False) -> None` | A link between a Group and a member object. |
| `keysight.ads.de.db_uu.GroupMember.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.GroupMember.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.GroupMember.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.GroupMember.group` | property | `` | The group that contains this member. |
| `keysight.ads.de.db_uu.GroupMember.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.GroupMember.is_leader` | property | `` | True if this member is the leader of the group. |
| `keysight.ads.de.db_uu.GroupMember.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.GroupMember.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.GroupMember.object` | property | `` | The object associated with this member. This may be None if the group contains objects that are not supported by ADS. |
| `keysight.ads.de.db_uu.GroupMember.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.GroupMember.props` | property | `` |  |
| `keysight.ads.de.db_uu.GroupMember.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.Instance.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Instance.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Instance.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.Instance.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Instance.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.Instance.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.Instance.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Instance.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.Instance.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.Instance.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.Instance.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.Instance.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Instance.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.Instance.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.Instance.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.Instance.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.Instance.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.Instance.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.Instance.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Instance.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.Instance.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Instance.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.InstanceIter.exclude_pin_insts` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstanceIter.include_pin_insts` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstAttrDisplay.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstAttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstAttrDisplay.layer` | property | `` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.pin` | property | `` |  |
| `keysight.ads.de.db_uu.InstAttrDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstAttrType` | class | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.CELL_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.IS_BOUND` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.LIB_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.NUM_BITS` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstAttrType.VIEW_NAME` | InstAttrType | `` | Members: LIB_NAME CELL_NAME VIEW_NAME NAME NUM_BITS IS_BOUND |
| `keysight.ads.de.db_uu.InstPin` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents the physical connection between an instance terminal and a pin on the master design. Note: There is no design object that represents an instance pin. This class is for convenience so you can find the snap p... |
| `keysight.ads.de.db_uu.InstPin.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this InstPin's InstTerm. This will also change the net of the InstTerm. |
| `keysight.ads.de.db_uu.InstPin.bbox` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.find_first_wire_label` | function | `(self) -> Optional[ForwardRef('AttrDisplay')]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.InstPin.get_angle_normalized` | function | `(self) -> int` |  |
| `keysight.ads.de.db_uu.InstPin.get_snap_layer_id` | function | `(self) -> keysight.ads.de.db._layer_id.LayerId` |  |
| `keysight.ads.de.db_uu.InstPin.inst_pin_id` | property | `` | The identifier for this InstPin. The id is typically the inst_term_id with additional information if the term is unbound or the master pin is missing. |
| `keysight.ads.de.db_uu.InstPin.inst_term` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.instance` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.is_valid` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.master_pin` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.net` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.net_label` | property | `` |  |
| `keysight.ads.de.db_uu.InstPin.snap_point` | property | `` |  |
| `keysight.ads.de.db_uu.InstPinIter` | class | `(obj: 'Net \| Instance \| InstTerm', term_or_bbox: Union[str, int, keysight.ads.de._points.BoxF, NoneType] = None) -> None` | An iterator for InstPins in a Design. |
| `keysight.ads.de.db_uu.InstPropDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstPropDisplay.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstPropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstPropDisplay.layer` | property | `` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.pin` | property | `` |  |
| `keysight.ads.de.db_uu.InstPropDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.InstTerm` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a connection between a net and a terminal in the master of an instance. If either the instance or term is multibit, the number of bits in the net must match the number of bits in the instance times the numb... |
| `keysight.ads.de.db_uu.InstTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.InstTerm.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this InstTerm. This will also change the net of this InstTerm. |
| `keysight.ads.de.db_uu.InstTerm.bits` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstTerm.find_first_wire_label` | function | `(self) -> Optional[ForwardRef('AttrDisplay')]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.InstTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.InstTerm.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.InstTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.InstTerm.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.inst_term_id` | property | `` | The unique identifier for this InstTerm. The id is of the form '<instance_name>.<term_id>' where <instance_name> is the name of the instance and <term_id> is either the term name or term number depending on how this I... |
| `keysight.ads.de.db_uu.InstTerm.instance` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.is_bound` | property | `` | Return True if this InstTerm is bound to the matching terminal on the master design. |
| `keysight.ads.de.db_uu.InstTerm.is_implicit` | property | `` | True if this InstTerm was implicitly created as part of a multi-bit InstTerm. |
| `keysight.ads.de.db_uu.InstTerm.is_numbered` | property | `` | Return True if this InstTerm binds to the terminal by number. |
| `keysight.ads.de.db_uu.InstTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.InstTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.InstTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.net_label` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.InstTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.term` | property | `` |  |
| `keysight.ads.de.db_uu.InstTerm.term_name` | property | `` | Return the term name if this InstTerm uses binds the term by name. Otherwise, raise an exception. |
| `keysight.ads.de.db_uu.InstTerm.term_number` | property | `` | Return the term number if this InstTerm binds the term by number. Otherwise, raise an exception. |
| `keysight.ads.de.db_uu.InstTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.InstTermAttrType` | class | `` | Members: NAME |
| `keysight.ads.de.db_uu.InstTermAttrType.NAME` | InstTermAttrType | `` | Members: NAME |
| `keysight.ads.de.db_uu.InstTermAttrType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.InstTermAttrType.value` | property | `` |  |
| `keysight.ads.de.db_uu.InstTermIter` | class | `(obj: 'Instance \| Net')` | An iterator for InstTerms in a Design. |
| `keysight.ads.de.db_uu.Interconnect` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | An Interconnect is a composite object used to implement a Trace. |
| `keysight.ads.de.db_uu.Interconnect.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Interconnect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Interconnect.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Interconnect. |
| `keysight.ads.de.db_uu.Interconnect.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Interconnect.members` | property | `` |  |
| `keysight.ads.de.db_uu.Keepout.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Keepout.affects_all_layers` | property | `` | True if this keepout affects all layers. |
| `keysight.ads.de.db_uu.Keepout.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Keepout.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.LayerId` | class | `(layer: Optional[int] = None, purpose: Optional[int] = None) -> None` |  |
| `keysight.ads.de.db_uu.LayerId.create_layer_id_from_library` | method | `(library: 'Library', layer_name: str, purpose_name: Optional[str] = None) -> 'LayerId'` |  |
| `keysight.ads.de.db_uu.LayerId.create_layer_id_from_library_name` | method | `(library_name: str, layer_name: str, purpose_name: Optional[str] = None) -> 'LayerId'` |  |
| `keysight.ads.de.db_uu.LayerId.layer` | property | `` |  |
| `keysight.ads.de.db_uu.LayerId.purpose` | property | `` |  |
| `keysight.ads.de.db_uu.LCVName.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.LimitRegionOption` | class | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MAY_TOUCH_ONLY_BOUNDING_BOX` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_CONTAIN_OBJECT` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_TOUCH_ACTUAL_OBJECT` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.LimitRegionOption.REGION_MUST_TOUCH_OBJECT_EDGE` | LimitRegionOption | `` | Members: REGION_MUST_CONTAIN_OBJECT REGION_MUST_TOUCH_ACTUAL_OBJECT REGION_MUST_TOUCH_OBJECT_EDGE REGION_MAY_TOUCH_ONLY_BOUNDING_BOX |
| `keysight.ads.de.db_uu.Line.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Line.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Line.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Line.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Line.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Line. |
| `keysight.ads.de.db_uu.Line.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Line.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Line.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Line.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Line.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.LineThickness` | class | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.MEDIUM` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.THICK` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineThickness.THIN` | LineThickness | `` | Members: THIN MEDIUM THICK |
| `keysight.ads.de.db_uu.LineTypeInfo.layer_id` | property | `` | The LayerId used by this LineTypeInfo. If line_item is set, the layer_id is ignored. Setting the layer_id will clear the LineItem. |
| `keysight.ads.de.db_uu.LineTypeInfo.line_item` | property | `` | The LineItem (from the technology) used by this LineTypeInfo. If line_item is not None, the layer_id is ignored. Setting the layer_id will clear the LineItem. |
| `keysight.ads.de.db_uu.LineTypeInfo.teardrop_definition_back` | property | `` | Returns a copy of the back teardrop definition. teardrop_definition_back is deprecated, and will be removed in the 2027 release. Use teardrop_back |
| `keysight.ads.de.db_uu.LineTypeInfo.teardrop_definition_front` | property | `` | Returns a copy of the front teardrop definition. teardrop_definition_front is deprecated, and will be removed in the 2027 release. Use teardrop_front |
| `keysight.ads.de.db_uu.MirrorType` | class | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.MIRROR_X` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.MIRROR_Y` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.MirrorType.NONE` | MirrorType | `` | Describes the mirroring of Instances. Members: NONE : 'None': Not mirrored. MIRROR_X : 'MirrorX': Mirrored about the X axis. MIRROR_Y : 'MirrorY': Mirrored about the Y axis. |
| `keysight.ads.de.db_uu.ModelCb` | class | `(callback_type: keysight.ads.de._pde.ModelCbType, callback: collections.abc.Callable) -> None` | A model callback that is implemented in Python. |
| `keysight.ads.de.db_uu.ModelCb.item_modified_callback` | function | `(callback: collections.abc.Callable[['Instance'], None]) -> 'ModelCb'` |  |
| `keysight.ads.de.db_uu.ModelCb.item_netlist_callback` | function | `(callback: collections.abc.Callable[['StandardInstance'], str]) -> 'ModelCb'` |  |
| `keysight.ads.de.db_uu.ModelCbAEL` | class | `(callback_type: keysight.ads.de._pde.ModelCbType, vocabulary: str, function: str, client_data: object, enabled: bool = True) -> None` | A model callback that is implemented in AEL. |
| `keysight.ads.de.db_uu.ModelCbBase` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for callbacks used by model definitions and model parameters. See :class:`de.db.ModelParam` and :class:`de.db.ModelDef`. Each callback function can be implemented in Python or AEL. |
| `keysight.ads.de.db_uu.ModelCbType` | class | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.ITEM_MODIFIED` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.ITEM_NETLIST` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.PARAMETER_DEFAULT_VALUE` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelCbType.PARAMETER_MODIFIED` | ModelCbType | `` | Specifies the purpose of a parameter callback. Members: PARAMETER_DEFAULT_VALUE : This type of callback returns a design specific default parameter value. PARAMETER_MODIFIED : This type of callback is called whenever ... |
| `keysight.ads.de.db_uu.ModelDef` | class | `(name: str, label: str) -> None` | A model definition implemented in Python. |
| `keysight.ads.de.db_uu.ModelDef.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDef.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDef.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelDefAEL` | class | `()` | A model definition implemented in AEL. |
| `keysight.ads.de.db_uu.ModelDefAEL.can_auto_increment` | property | `` | True if the first parameter of this model can be auto-incremented. |
| `keysight.ads.de.db_uu.ModelDefAEL.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefAEL.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefAEL.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelDefBase` | class | `()` | A model definition, sometimes referred to as an item definition or component definition, contains the parameter definitions for a particular component or design. |
| `keysight.ads.de.db_uu.ModelDefBase.is_bom_item` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefBase.is_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ModelDefBase.legacy_dialog_name` | property | `` | The name used by some components to determine which Parameter dialog to use for editing. |
| `keysight.ads.de.db_uu.ModelParamType` | class | `(*values)` | Create a collection of name/value pairs. Example enumeration: >>> class Color(Enum): ... RED = 1 ... BLUE = 2 ... GREEN = 3 Access them by: - attribute access: >>> Color.RED <Color.RED: 1> - value lookup: >>> Color(1)... |
| `keysight.ads.de.db_uu.ModelUnitType` | class | `(*values)` | Create a collection of name/value pairs. Example enumeration: >>> class Color(Enum): ... RED = 1 ... BLUE = 2 ... GREEN = 3 Access them by: - attribute access: >>> Color.RED <Color.RED: 1> - value lookup: >>> Color(1)... |
| `keysight.ads.de.db_uu.ModelUnitType.TEMPERATURE` | ModelUnitType | `` |  |
| `keysight.ads.de.db_uu.MomentumMesh.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.MomentumMesh.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.MomentumMesh.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Net` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for net objects. Nets represent logical connections between elements in a design. |
| `keysight.ads.de.db_uu.Net.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Net.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Net.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Net.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.Net.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.Net.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Net.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.NetAnnotData.net_name_layer` | property | `` | The default layer used for net name labels. |
| `keysight.ads.de.db_uu.NetAttrType` | class | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_EMPTY` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_GLOBAL` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.IS_IMPLICIT` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.NAME` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.NUM_BITS` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetAttrType.SIG_TYPE` | NetAttrType | `` | Members: NAME SIG_TYPE IS_GLOBAL IS_IMPLICIT IS_EMPTY NUM_BITS |
| `keysight.ads.de.db_uu.NetlistNode.is_grounded` | property | `` |  |
| `keysight.ads.de.db_uu.NetlistNode.pin_name` | property | `` |  |
| `keysight.ads.de.db_uu.NetlistNode.pin_number` | property | `` |  |
| `keysight.ads.de.db_uu.NullForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.OAParamType` | class | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.APP_PARAM` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.BOOLEAN` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.DOUBLE` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.FLOAT` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.INT` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.STRING` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.OAParamType.TIME` | OAParamType | `` | The type of an OAParam. Members: INT FLOAT STRING APP_PARAM : Application defined parameter holding typed data. DOUBLE BOOLEAN TIME |
| `keysight.ads.de.db_uu.open_design` | function | `(name: 'CellviewRefLike', mode: keysight.ads.de._pde.db.DesignMode \| str = <DesignMode.READ_ONLY: 0>) -> keysight.ads.de.db_uu._design.Design` | Open a design from an open library in the active workspace. Parameters ---------- name: CellviewRefLike The name of the design, usually of the form "LibraryName:CellName:schematic" mode: DesignMode \| str Specifies the... |
| `keysight.ads.de.db_uu.Orientation` | class | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MX` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MXR90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MY` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.MYR90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R0` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R180` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R270` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Orientation.R90` | Orientation | `` | Describes the orientation of Instance and Text objects. Members: R0 : 'R0': Not rotated or mirrored. R90 : 'R90': Rotated 90 degrees. R180 : 'R180': Rotated 180 degrees. R270 : 'R270': Rotated 270 degrees. MY : 'MY': ... |
| `keysight.ads.de.db_uu.Param.evaluate_no_expr` | function | `(self) -> str` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.Param.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.Param.item` | property | `` |  |
| `keysight.ads.de.db_uu.Param.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamBase` | class | `()` | Base class that holds both a parameter item and its definition. See :class:`ParamItem` and :class:`de.db.ModelParam`. |
| `keysight.ads.de.db_uu.ParamBase.evaluate_no_expr` | function | `(self) -> Union[str, list[str], list[list[str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamBase.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]], list[list[Union[bool, int, float, str]]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamBase.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamBase.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamCompound.display_value` | property | `` | Returns a list of copies of the sub parameter display values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_no_expr` | function | `(self) -> list[str]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str]]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamCompound.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamCompound.netlist_value` | property | `` | Returns a list of copies of the sub parameter netlist values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamCompound.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamCompound.value` | property | `` | Returns a list of copies of the sub parameter values. Do not attempt to assign values to individual elements of that list. Use sub_params if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamItem` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for parameter items. See also :class:`de.db.ModelParam` which is the parameter definition. The classes derived from ParamItem are used for default values in ModelParam and to hold instance and terminal para... |
| `keysight.ads.de.db_uu.ParamItem.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItem.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItem.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItem.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItem.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItem.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemCompound` | class | `(param_name: str, form_name: str, subparams: collections.abc.Sequence[keysight.ads.de.db._parameters.ParamItem]) -> None` | A parameter item that consists one or more sub-parameters. The number of sub-parameters must match the number of sub-parameters on the compound form that is used to create the parameter definition. The sub-parameters ... |
| `keysight.ads.de.db_uu.ParamItemCompound.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemCompound.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemCompound.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemCompound.sub_params` | property | `` | The sub-parameters (or fields) that define this compound parameter. |
| `keysight.ads.de.db_uu.ParamItemConst` | class | `(param_name: str, form: Union[str, keysight.ads.de.db._forms.Form, NoneType] = None) -> None` | A parameter item whose value is determined by its form - (see :class:`de.db.ConstForm`). |
| `keysight.ads.de.db_uu.ParamItemConst.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemConst.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemConst.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemConst.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemNull` | class | `(param_name: str) -> None` | A parameter item with no value. |
| `keysight.ads.de.db_uu.ParamItemNull.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemNull.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemNull.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemNull.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemNull.value` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated` | class | `(param_name: str, repeats: collections.abc.Sequence[keysight.ads.de.db._parameters.ParamItem]) -> None` | A parameter item that holds a list of one or more repeats. The parameter definition's formset dictates the forms that can be used for each repeat. A repeat cannot also be repeated but may use compound forms, having th... |
| `keysight.ads.de.db_uu.ParamItemRepeated.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemRepeated.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemRepeated.repeats` | property | `` | The repeats of this repeatable parameter. |
| `keysight.ads.de.db_uu.ParamItemString` | class | `(param_name: str, form: Union[str, keysight.ads.de.db._forms.Form, NoneType] = None, param_value: Optional[str] = None) -> None` | A string-valued parameter item. |
| `keysight.ads.de.db_uu.ParamItemString.clone` | function | `(self) -> 'ParamItem'` |  |
| `keysight.ads.de.db_uu.ParamItemString.form_name` | property | `` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_compound` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemCompound')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_const` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemConst')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_null` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemNull')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_repeated` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemRepeated')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.is_string` | function | `(p: 'ParamItem') -> TypeGuard[ForwardRef('ParamItemString')]` |  |
| `keysight.ads.de.db_uu.ParamItemString.name` | property | `` | The name of the parameter. The name should match the name of a parameter definition in the model. |
| `keysight.ads.de.db_uu.ParamItemString.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamItemString.value` | property | `` | The value of this ParamItem. When assigning values, prefer to use Param.value. |
| `keysight.ads.de.db_uu.ParamIter` | class | `(owner: 'InstanceDbu \| InstanceUu \| TermBaseDbu \| TermBaseUu') -> None` | An iterator that can be used to visit parameters of an instance or terminal. |
| `keysight.ads.de.db_uu.ParamIter.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_no_expr` | function | `(self) -> Union[str, list[str]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamNonRepeated.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamNonRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamRepeated.append_repeat` | function | `(self, value: Union[str, collections.abc.Sequence[str]]) -> None` | Clone the last repeat and set its value. append_repeat is deprecated, and will be removed in the 2027 release. Use: repeat = repeats.clone(value); repeat.value = value. |
| `keysight.ads.de.db_uu.ParamRepeated.display_value` | property | `` | Returns a list of copies of the repeat display values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_no_expr` | function | `(self) -> Union[list[str], list[list[str]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str, list[typing.Union[bool, int, float, str]]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamRepeated.item` | property | `` |  |
| `keysight.ads.de.db_uu.ParamRepeated.netlist_value` | property | `` | Returns a list of copies of the repeat netlist values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.ParamRepeated.no_plot` | property | `` | When True, this parameter will not be displayed in schematic view. |
| `keysight.ads.de.db_uu.ParamRepeated.value` | property | `` | Returns a list of copies of the repeat values. Do not attempt to assign values to individual elements of that list. Use repeats if you need to modify individual values. |
| `keysight.ads.de.db_uu.Path.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Path.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Path.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Path.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Path.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Path. |
| `keysight.ads.de.db_uu.Path.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Path.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Path.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Path.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Path.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PathSeg.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PathSeg.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PathSeg.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PathSeg.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PathSeg.layer` | property | `` |  |
| `keysight.ads.de.db_uu.PathSeg.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.PathSeg.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.PathSeg.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PathSeg.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PathStyle` | class | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.EXTEND` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.ROUND` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.TRUNCATE` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PathStyle.VARIABLE` | PathStyle | `` | Describes the end point styles of path objects. Members: TRUNCATE : 'Truncate': No extension beyond the end points. EXTEND : 'Extend': Extend the path by half the width. ROUND : 'Round': Extend the path with three edg... |
| `keysight.ads.de.db_uu.PCBBase.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBBase.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PCBBase.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBBase.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBBase.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBBase.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.PCBBase.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBBase.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBBase.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBBase.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.PCBBase.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBBase.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBBase.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBBase.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBBase.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBBase.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PCBBase.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBBase.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBBase.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad` | class | `(design: 'Design', master: 'CellviewRefLike \| Design', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None, mirror: Union[keysight.ads.de._pde.db.MirrorType, str, NoneType] = None) -> None` | Represents a PCB Pad instance in layout. The Pad can be a single layer pad, a pad with a specified drill layer, a pad with specified top and bottom layers, or a through pad. |
| `keysight.ads.de.db_uu.PCBPad.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBPad.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.bottom_layer` | property | `` | Bottom layer of this pad. Will raise an exception if this is not a pad with top and bottom layers. |
| `keysight.ads.de.db_uu.PCBPad.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBPad.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBPad.drill_layer` | property | `` | Drill layer of this pad. Will raise an exception if this is not a pad with drill. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBPad.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBPad.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBPad.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBPad.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.PCBPad.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBPad.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBPad.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBPad.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.PCBPad.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBPad.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBPad.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBPad.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.pad_layer` | property | `` | Layer of this pad. Will raise an exception if this is not a single layer pad. |
| `keysight.ads.de.db_uu.PCBPad.padstack_name` | property | `` | Name of the padstack template that defines this pad. The name will be in the form lib_name:padstack_name. |
| `keysight.ads.de.db_uu.PCBPad.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBPad.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PCBPad.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBPad.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBPad.top_layer` | property | `` | Top layer of this pad. Will raise an exception if this is not a pad with top and bottom layers. |
| `keysight.ads.de.db_uu.PCBPad.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia` | class | `(design: 'Design', master: 'CellviewRefLike \| Design', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, name: Optional[str] = None, angle: Optional[float] = None, mirror: Union[keysight.ads.de._pde.db.MirrorType, str, NoneType] = None) -> None` | Represents a PCB Via instance in layout. The Via can be specified by rule or with a Padstack template definition and specified layers. Vias with Padstack definitions can have a specified drill layer, specified top and... |
| `keysight.ads.de.db_uu.PCBVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PCBVia.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PCBVia.bottom_layer` | property | `` | Bottom layer of this via. Will raise an exception if this is not a via with top and bottom layers. |
| `keysight.ads.de.db_uu.PCBVia.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.PCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBVia.drill_layer` | property | `` | Drill layer of this via. Will raise an exception if this is not a via with drill. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBVia.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBVia.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.PCBVia.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.PCBVia.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.PCBVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.PCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBVia.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.PCBVia.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.PCBVia.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.PCBVia.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.PCBVia.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia.padstack_name` | property | `` | Name of the padstack template that defines this via. The name will be in the form lib_name:padstack_name. This will be empty if the via was defined by a rule. |
| `keysight.ads.de.db_uu.PCBVia.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.PCBVia.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PCBVia.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PCBVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PCBVia.rule_name` | property | `` | Name of the via rule that defines this via. The name will be in the form lib_name:rule_name. This will be empty if the via was not defined by a rule. |
| `keysight.ads.de.db_uu.PCBVia.top_layer` | property | `` | Top layer of this via. Will raise an exception if this is not a via with top and bottom layers. |
| `keysight.ads.de.db_uu.PCBVia.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.PCellInfo.reference_name` | property | `` | The reference name for reference PCells. |
| `keysight.ads.de.db_uu.PCellInfo.smart_mount_mapping_option` | property | `` | The mapping option for smart mount PCells. |
| `keysight.ads.de.db_uu.PCellInfo.supports_psn_behavior` | property | `` | True if the PCell supports PSN behavior. |
| `keysight.ads.de.db_uu.PCellInfo.supports_scaling` | property | `` | True if the PCell supports scaling. |
| `keysight.ads.de.db_uu.PCellType` | class | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.AEL_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.GENERIC` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.LAYER_MAPPING` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.LISP_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.MISSING` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.NONE` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PSN` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PYCELL` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.PYTHON_MACRO` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.REFERENCE` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.SMART_MOUNT` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.UNKNOWN` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.PCellType.VIA_PAD` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.Pin` | class | `(term: keysight.ads.de.db_uu._db_x.Term, pin_figs: Union[keysight.ads.de.db_uu._db_x.PinFig, list[keysight.ads.de.db_uu._db_x.PinFig]], *, angle: Optional[float] = None, add_annot: Optional[bool] = None) -> None` | Represents the physical connection between a terminal and a net. A pin can have zero or more PinFigs. Use PinFigIter(pin) to iterate over the pins. |
| `keysight.ads.de.db_uu.Pin.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Pin.add_label` | function | `(self, label: str, pt: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None, font_name: str = '', height: float = 0, align: keysight.ads.de._pde.db.TextAlignment \| str = <TextAlignment.LOWER_LEFT: 2>, orient: keysight.ads.de._pde.db.Orientation \| str = <Orientation.R0: 0>) -> 'AttrDisplay'` | Add a net name label to this Pin. This will also change the net of the pin's term. |
| `keysight.ads.de.db_uu.Pin.angle` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Pin.fig_group` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.find_first_wire_label` | function | `(self) -> Optional[keysight.ads.de.db_uu._db_x.AttrDisplay]` | find_first_wire_label is deprecated, and will be removed in the 2027 release. Use net_label instead. |
| `keysight.ads.de.db_uu.Pin.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.Pin.get_annotation_origin` | function | `(self) -> keysight.ads.de._points.PointF` | Calculate the annotation origin based on the pin attributes and parameters. |
| `keysight.ads.de.db_uu.Pin.get_default_annotation_origin` | function | `(self) -> keysight.ads.de._points.PointF` | Calculate the default annotation origin based on the pin attributes and parameters. |
| `keysight.ads.de.db_uu.Pin.get_pin_artifact_bbox_only` | function | `(self) -> keysight.ads.de._points.BoxF` |  |
| `keysight.ads.de.db_uu.Pin.get_pinfig_bbox` | function | `(self) -> keysight.ads.de._points.BoxF` |  |
| `keysight.ads.de.db_uu.Pin.get_pinfig_bbox_with_artifact` | function | `(self) -> keysight.ads.de._points.BoxF` |  |
| `keysight.ads.de.db_uu.Pin.get_primary_pin_fig` | function | `(self) -> Optional[keysight.ads.de.db_uu._db_x.PinFig]` |  |
| `keysight.ads.de.db_uu.Pin.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.Pin.has_ads_term_annotation` | property | `` | Return True if this Pin has ADS Name, Number or parameter annotation. |
| `keysight.ads.de.db_uu.Pin.has_any_pinfigs` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Pin.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.Pin.move_annotation` | function | `(self, offset: keysight.ads.de._points.PointF) -> None` | Move the annotation by the given offset. |
| `keysight.ads.de.db_uu.Pin.name` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.needs_drawing_artifact` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.net` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.net_label` | property | `` | Return the first net label (AttrDisplay) associated with this Pin. |
| `keysight.ads.de.db_uu.Pin.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.Pin.placement_status` | property | `` | PlacementStatus for this pin (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.Pin.props` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.snap_point` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.term` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.term_name` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.term_number` | property | `` |  |
| `keysight.ads.de.db_uu.Pin.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.Pin.update_pin_annotation` | function | `(self, annot_data: Optional[ForwardRef('PinAnnotData')] = None, *, preserve_origin: bool = True) -> None` | Update the pin annotation. If annot_data is None, the design preferences will be used. If preserve_origin is True, the annotation origin will not be moved. |
| `keysight.ads.de.db_uu.PinAnnotData` | class | `(obj: keysight.ads.de.db_uu._db_x.Pin \| keysight.ads.de.db_uu._design.Design) -> None` | Defines the information used to display annotation for Pins. This class is a value class, meaning the values are copies of the data that was extracted from a design or pin. |
| `keysight.ads.de.db_uu.PinAnnotData.collect_from_pin` | function | `(pin: keysight.ads.de.db_uu._db_x.Pin) -> 'PinAnnotData'` | Collect the annotation data from the pin. |
| `keysight.ads.de.db_uu.PinAnnotData.font_height` | property | `` | The font height used for annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.font_name` | property | `` | The font name used for annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.max_rows` | property | `` | The maximum number of rows used for parameter annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.param_layer` | property | `` | The layer used for parameter annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.precision` | property | `` | The precision used for parameter annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.term_name_layer` | property | `` | The layer used for term name annotation. |
| `keysight.ads.de.db_uu.PinAnnotData.term_number_layer` | property | `` | The layer used for term number annotation. |
| `keysight.ads.de.db_uu.PinFig` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for all figures that can represent pins (instances, shapes and vias). |
| `keysight.ads.de.db_uu.PinFig.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PinFig.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PinFig.bbox` | property | `` |  |
| `keysight.ads.de.db_uu.PinFig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PinFig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PinFig.find_first_wire_label` | function | `(self) -> Optional[ForwardRef('AttrDisplay')]` |  |
| `keysight.ads.de.db_uu.PinFig.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.PinFig.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.PinFig.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.PinFig.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.PinFig.net` | property | `` |  |
| `keysight.ads.de.db_uu.PinFig.net_is_sticky` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.PinFig.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.PinFig.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PinFig.props` | property | `` |  |
| `keysight.ads.de.db_uu.PinFig.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PinFig.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.PinFigIter` | class | `(pin: keysight.ads.de.db_uu._db_x.Pin) -> None` | An iterator for the PinFigs of a Pin. |
| `keysight.ads.de.db_uu.PinIter` | class | `(obj: keysight.ads.de.db_uu._design.Design \| keysight.ads.de.db_uu._db_x.Net \| keysight.ads.de.db_uu._db_x.Term) -> None` | An iterator for Pins in a Design. |
| `keysight.ads.de.db_uu.PlacementStatus` | class | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.FIXED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.LOCKED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.PlacementStatus.NONE` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.PLACED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.str` | property | `` | Return the string representation of the PlacementStatus. |
| `keysight.ads.de.db_uu.PlacementStatus.UNPLACED` | PlacementStatus | `` | Describes the placement status of certain design objects. Members: NONE : 'None': The placement status has not been set, but the current placement location is to be treated as valid. UNPLACED : 'Unplaced': The current... |
| `keysight.ads.de.db_uu.PlacementStatus.value` | property | `` |  |
| `keysight.ads.de.db_uu.Plane` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | A plane is a large shape (composite) on a single net. The layer is usually a conductor (e.g. copper). The net is often ground or power. |
| `keysight.ads.de.db_uu.Plane.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Plane.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Plane.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.Plane.members` | property | `` |  |
| `keysight.ads.de.db_uu.Plane.placement_status` | property | `` | PlacementStatus for this plane (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.PlaneInfo.layer_id` | property | `` | Specifies the layer and purpose of the Plane's shapes. |
| `keysight.ads.de.db_uu.PlaneInfo.min_island_area` | property | `` | Specifies the minimum area of an island that gets preserved when removing islands by area. |
| `keysight.ads.de.db_uu.PlaneInfo.remove_islands_mode` | property | `` | Determines how unconnected islands within the Plane's outline get removed. |
| `keysight.ads.de.db_uu.PlaneInfo.RemoveIslandsMode` | class | `` | Describes island removal. Members: REMOVE_NONE : 'RemoveNone': Does not remove any islands. REMOVE_ALL : 'RemoveAll: Removes all islands. REMOVE_BY_AREA : 'RemoveByArea': Removes islands whose area is less than the mi... |
| `keysight.ads.de.db_uu.PlaneInfo.same_props` | function | `(self, other: 'PlaneInfo') -> bool` | Determine if the essential properties are the same. This is not the same as equality because properties that are not enabled are ignored. |
| `keysight.ads.de.db_uu.PlaneInfo.smoothing_enabled` | property | `` | If True, the Plane's outline gets smoothed, possibly removing small features and rounding corners. |
| `keysight.ads.de.db_uu.PlaneInfo.use_round_corners_when_smoothing` | property | `` | If True, round corners created when features are removed by smoothing. Otherwise bevel the corners. |
| `keysight.ads.de.db_uu.Polygon.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Polygon.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Polygon.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Polygon.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Polygon.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Polygon. |
| `keysight.ads.de.db_uu.Polygon.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Polygon.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Polygon.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Polygon.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Polygon.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Polyline.empty` | property | `` |  |
| `keysight.ads.de.db_uu.PropDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.PropDisplay.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.PropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PropDisplay.layer` | property | `` |  |
| `keysight.ads.de.db_uu.PropDisplay.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.PropDisplay.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.PropDisplay.pin` | property | `` |  |
| `keysight.ads.de.db_uu.PropDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.PropType` | class | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.APP` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.BOOLEAN` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.DOUBLE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.DOUBLE_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.ENUM` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.FLOAT` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.FLOAT_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.HIER` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.INT` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.INT_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.STRING` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.TIME` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.PropType.TIME_RANGE` | PropType | `` | Members: INT INT_RANGE FLOAT FLOAT_RANGE STRING APP DOUBLE DOUBLE_RANGE BOOLEAN HIER TIME TIME_RANGE ENUM |
| `keysight.ads.de.db_uu.Rect.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Rect.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Rect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Rect.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Rect.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Rect.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Rect.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Rect.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Rect.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Ref.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Ref.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Ref.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ref.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ref.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Ref.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Ref.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.RefIter` | class | `(design: 'Design') -> None` | An iterator for Refs (Instance or Via references) in a Design. |
| `keysight.ads.de.db_uu.RepeatedForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.ScalarInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarInst.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.ScalarInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.ScalarInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ScalarInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ScalarInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.ScalarInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.ScalarInst.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.ScalarInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.ScalarInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.ScalarInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.ScalarInst.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.ScalarInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.ScalarInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ScalarInst.pin` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.ScalarInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ScalarInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.ScalarNet.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarNet.are_all_bits_of_net_global_ground` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarNet.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.ScalarNet.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarNet.is_empty_and_unlabeled` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarNet.is_global_ground` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm` | class | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> None` | A scalar term without bus-name syntax. |
| `keysight.ads.de.db_uu.ScalarTerm.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.ScalarTerm.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.ScalarTerm.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.ScalarTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarTerm.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.ScalarTerm.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.ScalarTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.ScalarTerm.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.ScalarTerm.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.ScalarTerm.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.ScalarTerm.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.ScalarTerm.name` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.net` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.ScalarTerm.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.ScalarTerm.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.ScalarTerm.props` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.ScalarTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.ScalarTerm.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.ScalarTerm.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.SecondaryTermInfo` | class | `(term_name: str, is_positive: bool)` | Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.is_positive` | property | `` | True if this term is a positive term. This is used to determine the polarity of the term in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.term_name` | property | `` | The name of the secondary term. |
| `keysight.ads.de.db_uu.Shape.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Shape.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Shape.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Shape.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Shape.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Shape.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Shape.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Shape.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Shape.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.exclude_invisible_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.exclude_protected_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.include_invisible_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.include_protected_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.is_pin_or_net_iteration` | property | `` |  |
| `keysight.ads.de.db_uu.ShapeIter.limit_layer` | function | `(self, layer: int) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIter.limit_layerid` | function | `(self, layer_id: keysight.ads.de.db._layer_id.LayerId) -> None` |  |
| `keysight.ads.de.db_uu.ShapeIterNetOption` | class | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeIterNetOption.NET_SHAPES_ONLY` | ShapeIterNetOption | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeIterNetOption.PIN_AND_NET_SHAPES` | ShapeIterNetOption | `` | Members: NET_SHAPES_ONLY PIN_AND_NET_SHAPES |
| `keysight.ads.de.db_uu.ShapeOption` | class | `` | Members: ALL_SHAPES |
| `keysight.ads.de.db_uu.ShapeOption.ALL_SHAPES` | ShapeOption | `` | Members: ALL_SHAPES |
| `keysight.ads.de.db_uu.SignalType` | class | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.ANALOG` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.CLOCK` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.GROUND` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.POWER` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.RESET` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.SCAN` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.SIGNAL` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_HI` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_LO` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.SignalType.TIE_OFF` | SignalType | `` | Describes the different uses of a net. Members: SIGNAL : 'Signal': Signal - the 'normal' type. POWER : 'Power': Power net. GROUND : 'Ground': Ground net. CLOCK : 'Clock': Clock net. TIE_OFF : 'TieOff': Tie-off net. TI... |
| `keysight.ads.de.db_uu.StackedPCBVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.StackedPCBVia.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.StackedPCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StackedPCBVia.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.StackedPCBVia.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.StackedPCBVia.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.StackedPCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.StackedPCBVia.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.PadViaType` | class | `` | Type of Pad or Via. Members: SINGLE_LAYER_PAD DRILL_LAYER THROUGH BLIND_BURIED_PAD |
| `keysight.ads.de.db_uu.StackedPCBVia.pin` | property | `` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.StackedPCBVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.StackedPCBVia.rule_name` | property | `` | Name of the via rule that defines this via. The name will be in the form lib_name:rule_name. This will be empty if the via was not defined by a rule. |
| `keysight.ads.de.db_uu.StackedPCBVia.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.std_string_param` | function | `(value: str) -> keysight.ads.de.db._parameters.ParamItemString` | Make a ParamItemString using the StdForm. |
| `keysight.ads.de.db_uu.StdVia.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.StdVia.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.StdVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StdVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StdVia.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.StdVia.pin` | property | `` |  |
| `keysight.ads.de.db_uu.StdVia.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.StringForm.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.StringFormWithAELCallbacks.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.StringFormWithCallbacks.dialog_data` | property | `` | A string used by edit dialogs for this form. If this string is empty, the name of the form will be used by default. |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle` | class | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.NONE` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.TEARDROP_ANGLE` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.WIDTH_AND_HEIGHT` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropDefinitionStyle.WIDTH_TANGENT` | TeardropDefinitionStyle | `` | Members: NONE WIDTH_AND_HEIGHT WIDTH_TANGENT TEARDROP_ANGLE |
| `keysight.ads.de.db_uu.TeardropValueUnits` | class | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.DB_UNITS` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.RATIO` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.TeardropValueUnits.VALUE` | TeardropValueUnits | `` | Determines how a teardrop value is specified (ratio or absolute value). Members: VALUE : 'Value': The value is specified as an absolute value. DB_UNITS : 'Value': Deprecated alias for VALUE. RATIO : 'Ratio': The value... |
| `keysight.ads.de.db_uu.Term` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Terminals represent a logical connection points for a design. The pins associated with terminals represent the physical connection points. The nets associated with terminals through the terminals to the parent design.... |
| `keysight.ads.de.db_uu.Term.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Term.create` | function | `(net: keysight.ads.de.db_uu._db_x.Net, name: str, term_type: keysight.ads.de._pde.db.TermType \| str = <TermType.INPUT_OUTPUT: 2>, *, number: int = 0) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Term.create_connect_def` | function | `(self, net_expression: str) -> None` |  |
| `keysight.ads.de.db_uu.Term.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Term.find_prop` | function | `(self, name: str) -> Optional[ForwardRef('Property')]` |  |
| `keysight.ads.de.db_uu.Term.groups` | property | `` | The collection of groups that contain this object. |
| `keysight.ads.de.db_uu.Term.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.Term.is_implicit` | property | `` | True if this term was implicitly created. For example, if the BusTerm "P<0:1>" was created explicitly, then BusTermBits "P<0>" and "P<1>" will be created implicitly. |
| `keysight.ads.de.db_uu.Term.is_part_of_composite_object` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.Term.library` | property | `` | The library of the design that contains this object. |
| `keysight.ads.de.db_uu.Term.model_def` | property | `` | Returns the model definition shared by all Terms. |
| `keysight.ads.de.db_uu.Term.name` | property | `` |  |
| `keysight.ads.de.db_uu.Term.net` | property | `` |  |
| `keysight.ads.de.db_uu.Term.number` | property | `` | By default, terminals connect by name and this number is 0. If the number is greater than zero, it represents the netlisting order for this terminal. |
| `keysight.ads.de.db_uu.Term.parameters` | property | `` |  |
| `keysight.ads.de.db_uu.Term.parent` | property | `` | The design that contains this object. |
| `keysight.ads.de.db_uu.Term.pins` | property | `` | The collection of physical pins associated with this Term. Note that a Term can have zero or more pins. |
| `keysight.ads.de.db_uu.Term.props` | property | `` |  |
| `keysight.ads.de.db_uu.Term.ref_plane_shift_dbu` | property | `` |  |
| `keysight.ads.de.db_uu.Term.ref_plane_shift_meters` | property | `` |  |
| `keysight.ads.de.db_uu.Term.rename_term` | function | `(self, name: str) -> 'Term'` |  |
| `keysight.ads.de.db_uu.Term.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.Term.term_type` | property | `` |  |
| `keysight.ads.de.db_uu.Term.type` | property | `` | Describes the type of this object. Note, this is not the same as the Python type. For that, use type(shape) rather than shape.type. |
| `keysight.ads.de.db_uu.TermAttrType` | class | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.HAS_PINS` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.NAME` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.TermAttrType.NUM_BITS` | TermAttrType | `` | Describes Term attributes. Members: NAME : 'Name': The name of the Term. HAS_PINS : 'HasPins': Whether the Term has Pins. NUM_BITS : 'NumBits': The number of bits in the Term. |
| `keysight.ads.de.db_uu.TermAttrType.str` | property | `` | Return the string representation of the TermAttrType. |
| `keysight.ads.de.db_uu.TermAttrType.value` | property | `` |  |
| `keysight.ads.de.db_uu.TermIter` | class | `(obj: 'Design \| Net') -> None` | An iterator for Terms in a Design. |
| `keysight.ads.de.db_uu.TermType` | class | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.INPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.INPUT_OUTPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.JUMPER` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.db_uu.TermType.OUTPUT` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.str` | property | `` | Return the string representation of the TermType. |
| `keysight.ads.de.db_uu.TermType.SWITCH` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.TRISTATE` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.UNUSED` | TermType | `` | Describes the different uses of a Term. Members: INPUT : 'Input': Input Term. OUTPUT : 'Output': Output Term. INPUT_OUTPUT : 'InputOutput': Input/Output Term. SWITCH : 'Switch': Switch Term. JUMPER : 'Jumper': Jumper ... |
| `keysight.ads.de.db_uu.TermType.value` | property | `` |  |
| `keysight.ads.de.db_uu.Text.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Text.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Text.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Text.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Text.layer` | property | `` |  |
| `keysight.ads.de.db_uu.Text.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.Text.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.Text.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Text.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextAlignment` | class | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.CENTER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.LOWER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_CENTER` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_LEFT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextAlignment.UPPER_RIGHT` | TextAlignment | `` | Describes the alignment of Text objects. Members: UPPER_LEFT : 'UpperLeft': Origin is at the upper left of the text. CENTER_LEFT : 'CenterLeft': Origin is at the center left of the text. LOWER_LEFT : 'LowerLeft': Orig... |
| `keysight.ads.de.db_uu.TextBase.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextBase.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.TextBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextBase.layer` | property | `` |  |
| `keysight.ads.de.db_uu.TextBase.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.TextBase.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.TextBase.pin` | property | `` |  |
| `keysight.ads.de.db_uu.TextBase.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextDisplay.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextDisplay.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.TextDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextDisplay.layer` | property | `` |  |
| `keysight.ads.de.db_uu.TextDisplay.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.TextDisplay.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.TextDisplay.pin` | property | `` |  |
| `keysight.ads.de.db_uu.TextDisplay.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.TextDisplayFormat` | class | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.NAME` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.NAME_VALUE` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextDisplayFormat.VALUE` | TextDisplayFormat | `` | Describes the format of Text Displays. Members: NAME : 'Name': Display the name only. VALUE : 'Value': Display the value only. NAME_VALUE : 'NameValue': Display the name and value. |
| `keysight.ads.de.db_uu.TextOverride` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | A text object that supports overriding text from an instance master. |
| `keysight.ads.de.db_uu.TextOverride.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.TextOverride.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.TextOverride.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextOverride.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextOverride.layer` | property | `` |  |
| `keysight.ads.de.db_uu.TextOverride.layer_id` | property | `` |  |
| `keysight.ads.de.db_uu.TextOverride.move_to_layer_id` | function | `(shape: 'Shape', layer_id: keysight.ads.de.db._layer_id.LayerId) -> 'Shape'` |  |
| `keysight.ads.de.db_uu.TextOverride.pin` | property | `` |  |
| `keysight.ads.de.db_uu.TextOverride.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.Transaction` | class | `(design: 'Design \| DesignDb', command: str = 'Edit') -> None` | Operations performed between when the Transaction is created and when it is committed may be undone. This provides the ability to group multiple operations together and undo them with a call to rollback. |
| `keysight.ads.de.db_uu.Transaction.is_empty` | function | `(self) -> bool` |  |
| `keysight.ads.de.db_uu.TransactionState` | class | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.COMMITTED` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.IN_PROGRESS` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.TransactionState.ROLLED_BACK` | TransactionState | `` | Specifies the state of a design transaction. Members: IN_PROGRESS : The transaction is in progress. COMMITTED : The transaction has been committed. ROLLED_BACK : The transaction has been rolled back. |
| `keysight.ads.de.db_uu.VectorInst.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.VectorInst.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.VectorInst.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.VectorInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInst.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInst.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInst.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.VectorInst.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.VectorInst.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.VectorInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.VectorInst.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInst.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.VectorInst.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.VectorInst.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInst.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.VectorInst.pin` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInst.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.VectorInst.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.VectorInst.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.VectorInstBit.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.create_from_item` | function | `(design: 'Design', master: 'ItemInfo', origin: Union[keysight.ads.de._points.PointF, tuple[float, float]], *, angle: float = 0.0, mirror: keysight.ads.de._pde.db.MirrorType \| str = <MirrorType.NONE: 0>, ads_annot: bool \| None = None) -> 'Instance'` |  |
| `keysight.ads.de.db_uu.VectorInstBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInstBit.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInstBit.find_inst_term_named` | function | `(self, name: str) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given name if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInstBit.find_inst_term_numbered` | function | `(self, number: int) -> Optional[keysight.ads.de.db_uu._db_x.InstTerm]` | Return the InstTerm bound to the given number if found, otherwise return None. |
| `keysight.ads.de.db_uu.VectorInstBit.get_inst_pin_iter` | function | `(self) -> 'InstPinIter'` |  |
| `keysight.ads.de.db_uu.VectorInstBit.get_inst_term_iter` | function | `(self) -> 'InstTermIter'` |  |
| `keysight.ads.de.db_uu.VectorInstBit.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.VectorInstBit.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_pins` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInstBit.inst_term_named` | function | `(self, name: str) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given name. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_term_numbered` | function | `(self, number: int) -> keysight.ads.de.db_uu._db_x.InstTerm` | Return the InstTerm bound to the given number. |
| `keysight.ads.de.db_uu.VectorInstBit.inst_terms` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInstBit.invoke_item_parameter_changed_callback` | function | `(self, parameter_names: str \| collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.pin` | property | `` |  |
| `keysight.ads.de.db_uu.VectorInstBit.placement_status` | property | `` | PlacementStatus for this instance (e.g. Fixed or Locked). |
| `keysight.ads.de.db_uu.VectorInstBit.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.VectorInstBit.update_item_annotation` | function | `(self, annot_data: Optional[ForwardRef('AnnotData')] = None) -> None` |  |
| `keysight.ads.de.db_uu.Via` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for OpenAccess Vias. A via represents a physical connection between traces (also PathSegs and Rountes) that are on two different layers. Vias are defined by a definition in the technology. |
| `keysight.ads.de.db_uu.Via.add_child_to_parent_group` | function | `(self, child: 'ApolloObject') -> None` | Create a parent-child relationship with this object as the parent. This object will become the leader of the group and the given child will be a member. |
| `keysight.ads.de.db_uu.Via.add_to_pin` | function | `(self, pin: 'Pin') -> None` |  |
| `keysight.ads.de.db_uu.Via.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Via.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Via.get_placement_transform` | function | `(self) -> keysight.ads.de.db._genpolyline.Transform` | Return a copy of the placement transform for this object. |
| `keysight.ads.de.db_uu.Via.pin` | property | `` |  |
| `keysight.ads.de.db_uu.Via.remove_from_pin` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement` | class | `(names: collections.abc.Sequence[str] = []) -> None` | ViaElement identifies the Via inside an Interconnect. |
| `keysight.ads.de.db_uu.ViaElement.add_via_name` | function | `(self, name: str) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.add_via_names` | function | `(self, names: collections.abc.Sequence[str]) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.clear_vias` | function | `(self) -> None` |  |
| `keysight.ads.de.db_uu.ViaElement.is_empty` | property | `` |  |
| `keysight.ads.de.db_uu.ViaElement.via_names` | property | `` |  |
| `keysight.ads.de.db_uu.ViaIterNetOptions` | class | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.ViaIterNetOptions.NET_VIAS_ONLY` | ViaIterNetOptions | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.ViaIterNetOptions.PIN_AND_NET_VIAS` | ViaIterNetOptions | `` | Members: NET_VIAS_ONLY PIN_AND_NET_VIAS |
| `keysight.ads.de.db_uu.WhichConnection` | class | `` | Members: BEGIN END |
| `keysight.ads.de.db_uu.WhichConnection.BEGIN` | WhichConnection | `` | Members: BEGIN END |
| `keysight.ads.de.db_uu.WhichConnection.END` | WhichConnection | `` | Members: BEGIN END |

### `keysight.ads.de.tech`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.tech.DerivedLayer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a derived layer. A derived layer is a (virtual) layer that is formed by operations on shapes from one or more other layers. Derived layers typically don't have any shapes. |
| `keysight.ads.de.tech.DerivedLayer.abbreviation` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.create_boolean_layer` | function | `(tech: 'Tech', layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, layer2: keysight.ads.de.tech._tech.Layer \| str) -> 'DerivedLayer'` | Create a derived layer from two source layers and boolean operation. The derived layer contains all the shapes that result by performing the boolean operation on all the shapes from the two source layers. |
| `keysight.ads.de.tech.DerivedLayer.create_sizing_layer` | function | `(tech: 'Tech', layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, distance: int) -> 'DerivedLayer'` | Create a derived layer from a single source layer, a sizing operation, and a distance parameter. The derived layer contains all the shapes that result by performing the sizing operation on all the shapes from the sour... |
| `keysight.ads.de.tech.DerivedLayer.get_distance_param` | function | `(self) -> int` | Return the distance parameter from this derived layer. This only works for derived layers that use a sizing operation. If you call this function on a derived layer that does not have a distance parameter, it will rais... |
| `keysight.ads.de.tech.DerivedLayer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.tech.DerivedLayer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.tech.DerivedLayer.layer1` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.layer1_num` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.layer2` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.layer2_num` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.layer_binding` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.library` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.name` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.number` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.operation` | property | `` | Returns the derived layer operation. NOTE: If this is a user defined operation (USER_DEFINED), you must use operation_name to get the name of the operation. |
| `keysight.ads.de.tech.DerivedLayer.operation_name` | property | `` | Returns the name of the derived layer operation. |
| `keysight.ads.de.tech.DerivedLayer.process_role` | property | `` |  |
| `keysight.ads.de.tech.DerivedLayer.tech` | property | `` |  |
| `keysight.ads.de.tech.InteropType` | class | `` | Describes the interoperability of technology. Members: UNSPECIFIED : 'Unspecified': Interoperability will be determined based on technology contents. LEGACY : 'Legacy': Colors, fill patterns and line styles are define... |
| `keysight.ads.de.tech.InteropType.INTEROPERABLE` | InteropType | `` | Describes the interoperability of technology. Members: UNSPECIFIED : 'Unspecified': Interoperability will be determined based on technology contents. LEGACY : 'Legacy': Colors, fill patterns and line styles are define... |
| `keysight.ads.de.tech.InteropType.LEGACY` | InteropType | `` | Describes the interoperability of technology. Members: UNSPECIFIED : 'Unspecified': Interoperability will be determined based on technology contents. LEGACY : 'Legacy': Colors, fill patterns and line styles are define... |
| `keysight.ads.de.tech.InteropType.UNSPECIFIED` | InteropType | `` | Describes the interoperability of technology. Members: UNSPECIFIED : 'Unspecified': Interoperability will be determined based on technology contents. LEGACY : 'Legacy': Colors, fill patterns and line styles are define... |
| `keysight.ads.de.tech.Layer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Base class for Layer objects in Tech. Layer objects become invalid when the technology is modified. So the Python objects should have a short lifetime. |
| `keysight.ads.de.tech.Layer.abbreviation` | property | `` |  |
| `keysight.ads.de.tech.Layer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.tech.Layer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.tech.Layer.layer_binding` | property | `` |  |
| `keysight.ads.de.tech.Layer.library` | property | `` |  |
| `keysight.ads.de.tech.Layer.name` | property | `` |  |
| `keysight.ads.de.tech.Layer.number` | property | `` |  |
| `keysight.ads.de.tech.Layer.process_role` | property | `` |  |
| `keysight.ads.de.tech.Layer.tech` | property | `` |  |
| `keysight.ads.de.tech.LayerOp` | class | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.AND` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.AREA` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.AVOIDING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.BUTTING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.BUTTING_OR_COINCIDENT` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.BUTTING_OR_OVERLAPPING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.BUTTONLY` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.COINCIDENT` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.COINCIDENT_ONLY` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.GROW` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.GROW_HORIZONTAL` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.GROW_VERTICAL` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.INSIDE` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.is_boolean` | property | `` | True if the operation is a boolean operation. |
| `keysight.ads.de.tech.LayerOp.is_sizing` | property | `` | True if the operation is a size operation. |
| `keysight.ads.de.tech.LayerOp.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.tech.LayerOp.NOT` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.OR` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.OUTSIDE` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.OVERLAPPING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.SELECT` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.SHRINK` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.SHRINK_HORIZONTAL` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.SHRINK_VERTICAL` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.str` | property | `` | Return the string used as the operation name. |
| `keysight.ads.de.tech.LayerOp.STRADDLING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.TOUCHING` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.USER_DEFINED` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerOp.value` | property | `` |  |
| `keysight.ads.de.tech.LayerOp.XOR` | LayerOp | `` | Defines the type of a derived layer operation. Members: AND : Boolean operation OR : Boolean operation NOT : Boolean operation XOR : Boolean operation TOUCHING BUTTONLY USER_DEFINED : Don't use this for a derived laye... |
| `keysight.ads.de.tech.LayerSlice` | class | `(library: Optional[keysight.ads.de._core.library.Library] = None, layer: Union[str, keysight.ads.de.db._layer_id.LayerId, NoneType] = None, enclosure_width_uu: Optional[float] = None) -> None` | Represents a single slice of a LineStrip. Identifies the layer for this slice and its enclosure. |
| `keysight.ads.de.tech.LayerSlice.create_from_layer_id` | method | `(library: keysight.ads.de._core.library.Library, layer_id: keysight.ads.de.db._layer_id.LayerId, enclosure_width: float) -> 'LayerSlice'` |  |
| `keysight.ads.de.tech.LayerSlice.create_from_names` | method | `(library: keysight.ads.de._core.library.Library, layer_name: str, purpose_name: str, enclosure_width: float) -> 'LayerSlice'` |  |
| `keysight.ads.de.tech.LayerSlice.enclosure_width_uu` | property | `` | Return the difference in width (in user units) between this slice and the default width of the strip. |
| `keysight.ads.de.tech.LayerSlice.layer_id` | property | `` |  |
| `keysight.ads.de.tech.LayerSlice.layer_name` | property | `` |  |
| `keysight.ads.de.tech.LayerSlice.purpose_name` | property | `` |  |
| `keysight.ads.de.tech.LayerSlice.validate_names_and_id` | function | `(self, library: keysight.ads.de._core.library.Library) -> None` | Check that the layer_id matches the layer and purpose names. |
| `keysight.ads.de.tech.LineBeginEndTypes` | class | `(*args, **kwargs)` | Deprecated. Use LineEndType instead. LineBeginEndTypes is deprecated, and will be removed in the 2027 release. Use LineEndType |
| `keysight.ads.de.tech.LineBeginEndTypes.CHAMFER` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.CHAMFERED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.EXTEND` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.EXTENDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.ROUND` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.ROUNDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.TRUNCATE` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineBeginEndTypes.TRUNCATED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineClearance.layer_name` | property | `` |  |
| `keysight.ads.de.tech.LineCornerType` | class | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerType.ADAPTIVE_MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerType.CURVED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerType.MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerType.ROUND` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerType.SQUARE` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes` | class | `(*args, **kwargs)` | Deprecated. Use LineCornerType instead. LineCornerTypes is deprecated, and will be removed in the 2027 release. Use LineCornerType |
| `keysight.ads.de.tech.LineCornerTypes.ADAPTIVE_MITER_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.ADAPTIVE_MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.CURVE_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.CURVED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.MITERED` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.MITERED_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.ROUND` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.ROUND_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.SQUARE` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineCornerTypes.SQUARE_CORNER` | LineCornerType | `` | Defines the type of corner used by LineTypeInfo. Members: SQUARE : 'Square': The line has square corners. MITERED : 'Mitered': The line has mitered corners - prefer ADAPTIVE_MITERED. ADAPTIVE_MITERED : 'AdaptiveMitere... |
| `keysight.ads.de.tech.LineEndType` | class | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineEndType.CHAMFERED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineEndType.EXTENDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineEndType.ROUNDED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineEndType.TRUNCATED` | LineEndType | `` | Defines the type of ending used by a LineItem. Members: TRUNCATED : 'Truncated': The line ends are truncated. EXTENDED : 'Extended': The line ends are extended. CHAMFERED : 'Chamfered': The line ends are chamfered. RO... |
| `keysight.ads.de.tech.LineItem` | class | `(name: Optional[str] = None) -> None` | Defines transmission line types. A LineItem must be saved in a library in order to be used by layout designs. |
| `keysight.ads.de.tech.LineItem.add_clearance` | function | `(self, clearance: keysight.ads.de.tech._tech.LineClearance) -> None` |  |
| `keysight.ads.de.tech.LineItem.begin_end_type` | property | `` | The type of ending (and beginning) of lines defined by this line item. |
| `keysight.ads.de.tech.LineItem.clearances` | property | `` | The collection of line clearances in this LineItem. |
| `keysight.ads.de.tech.LineItem.corner` | property | `` | Defines the corners (bends) of lines defined by this line item. |
| `keysight.ads.de.tech.LineItem.description` | property | `` | Description of this line type definition used by tooltips. |
| `keysight.ads.de.tech.LineItem.get_calculated_type_deprecated` | function | `(self) -> str` |  |
| `keysight.ads.de.tech.LineItem.is_single_strip_line` | property | `` |  |
| `keysight.ads.de.tech.LineItem.name` | property | `` | Name of this line type definition. References to line items by layout objects use this name. |
| `keysight.ads.de.tech.LineItem.plane_layer_names` | property | `` | The collection of plane layer names used by this line item. |
| `keysight.ads.de.tech.LineItem.simulation_model` | property | `` |  |
| `keysight.ads.de.tech.LineItem.single_strip_line` | property | `` | The only strip item if this line is single-strip. Will raise an exception if this line is not single-strip. |
| `keysight.ads.de.tech.LineItem.strip_items` | property | `` | The collection of line strips in this LineItem. |
| `keysight.ads.de.tech.LineItem.substrate` | property | `` | Name of the substrate used by this Line type definition. |
| `keysight.ads.de.tech.LineItem.type` | property | `` | Legacy type - not really used now. |
| `keysight.ads.de.tech.LineItem.uses_layer_id` | function | `(self, layer_id: keysight.ads.de.db._layer_id.LayerId) -> bool` |  |
| `keysight.ads.de.tech.LineStripItem` | class | `(library: Optional[keysight.ads.de._core.library.Library] = None, layer_name: Optional[str] = None, purpose_name: Optional[str] = None, layer_id: Optional[keysight.ads.de.db._layer_id.LayerId] = None) -> None` | Represents a single strip of a line type. |
| `keysight.ads.de.tech.LineStripItem.add_layer_slice` | function | `(self, library: keysight.ads.de._core.library.Library, layer_name: str, purpose_name: str, width: float = 0.0) -> None` | Create a LayerSlice and append it to layer_slices. |
| `keysight.ads.de.tech.LineStripItem.default_width` | property | `` | The default width (in user units) of the layer slices. |
| `keysight.ads.de.tech.LineStripItem.has_multiple_slices` | property | `` |  |
| `keysight.ads.de.tech.LineStripItem.layer_slices` | property | `` | Return the collection of layer slices in this LineStripItem. |
| `keysight.ads.de.tech.LineStripItem.strip_id` | property | `` |  |
| `keysight.ads.de.tech.LineStripItem.strip_spacing_type` | property | `` | Returns the type of spacing required between this strip and the next strip. |
| `keysight.ads.de.tech.LineStripItem.strip_spacing_value` | property | `` | Returns the spacing required between this strip and the next strip. |
| `keysight.ads.de.tech.LineStripItem.uses_layer_id` | function | `(self, layer_id: keysight.ads.de.db._layer_id.LayerId) -> bool` | Return True if any LayerSlice is on the given layer. |
| `keysight.ads.de.tech.LineStripSpacingType` | class | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingType.CENTER_LINE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingType.EDGE_TO_EDGE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingType.NO_SPACING` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingTypes` | class | `(*args, **kwargs)` | LineStripSpacingTypes is deprecated, and will be removed in the 2027 release. Use LineStripSpacingType |
| `keysight.ads.de.tech.LineStripSpacingTypes.CENTER_LINE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingTypes.EDGE_TO_EDGE` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineStripSpacingTypes.NO_SPACING` | LineStripSpacingType | `` | Defines the type of spacing between line strips. Members: NO_SPACING : 'NoSpacing': The line strip items have no spacing. EDGE_TO_EDGE : 'EdgeToEdge': The line strips use edge-to-edge spacing. CENTER_LINE : 'CenterLin... |
| `keysight.ads.de.tech.LineTypeSimulationModel.use_single_tline_element_to_model_a_trace` | property | `` |  |
| `keysight.ads.de.tech.OAMaterial` | class | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.CONTACTLESS_METAL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.CUT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.METAL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.N_DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.N_IMPLANT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.N_WELL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.OTHER` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.P_DIFF` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.P_IMPLANT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.P_WELL` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.PASSIVATION_CUT` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.POLY` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.OAMaterial.RECOGNITION` | OAMaterial | `` | Members: OTHER N_WELL P_WELL N_DIFF P_DIFF N_IMPLANT P_IMPLANT POLY CUT METAL CONTACTLESS_METAL DIFF RECOGNITION PASSIVATION_CUT |
| `keysight.ads.de.tech.PhysicalLayer` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a physical layer (one that contains shapes and figures). |
| `keysight.ads.de.tech.PhysicalLayer.abbreviation` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.create` | function | `(tech: 'Tech', layer_name: str, layer_num: int) -> 'PhysicalLayer'` |  |
| `keysight.ads.de.tech.PhysicalLayer.is_derived` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('DerivedLayer')]` |  |
| `keysight.ads.de.tech.PhysicalLayer.is_physical` | function | `(layer: 'Layer') -> TypeGuard[ForwardRef('PhysicalLayer')]` |  |
| `keysight.ads.de.tech.PhysicalLayer.layer_binding` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.library` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.mask_number` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.material` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.mfg_grid` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.name` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.number` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.process_role` | property | `` |  |
| `keysight.ads.de.tech.PhysicalLayer.tech` | property | `` |  |
| `keysight.ads.de.tech.ProcessRole` | class | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.ANNOT_COMPONENT_NAME` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.ANNOT_INSTANCE_NAME` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.ANNOT_OTHER` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.BOUNDARY` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.COMPONENT_BODY` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.CONDUCTOR` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.CONDUCTOR_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.CONDUCTOR_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.DIELECTRIC` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.DIELECTRIC_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.DIELECTRIC_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.DRC` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.HEAT_SOURCE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.NONE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.NOT_DEFINED` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.OTHER` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SCRATCH` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SEMICONDUCTOR` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SEMICONDUCTOR_SLOT` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SEMICONDUCTOR_VIA` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SILK_SCREEN` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SOLDER_MASK` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.ProcessRole.SOLDER_PASTE` | ProcessRole | `` | Describes the role of a layer - the meaning of shapes on that layer. Members: NOT_DEFINED : 'NotDefined': The layer has no process role defined so shapes have no meaning. NONE : 'NotDefined': Deprecated alias for NOT_... |
| `keysight.ads.de.tech.SmartMountAlignmentType` | class | `` | Defines the alignment of a SmartMount PCell. Members: AUTOMATIC : 'Automatic': The alignment is determined automatically. CHIP_LAYER : 'ChipLayer': The Chip layer is on top of the mount layer. CHIP_INTERFACE : 'ChipIn... |
| `keysight.ads.de.tech.SmartMountAlignmentType.AUTOMATIC` | SmartMountAlignmentType | `` | Defines the alignment of a SmartMount PCell. Members: AUTOMATIC : 'Automatic': The alignment is determined automatically. CHIP_LAYER : 'ChipLayer': The Chip layer is on top of the mount layer. CHIP_INTERFACE : 'ChipIn... |
| `keysight.ads.de.tech.SmartMountAlignmentType.CHIP_INTERFACE` | SmartMountAlignmentType | `` | Defines the alignment of a SmartMount PCell. Members: AUTOMATIC : 'Automatic': The alignment is determined automatically. CHIP_LAYER : 'ChipLayer': The Chip layer is on top of the mount layer. CHIP_INTERFACE : 'ChipIn... |
| `keysight.ads.de.tech.SmartMountAlignmentType.CHIP_LAYER` | SmartMountAlignmentType | `` | Defines the alignment of a SmartMount PCell. Members: AUTOMATIC : 'Automatic': The alignment is determined automatically. CHIP_LAYER : 'ChipLayer': The Chip layer is on top of the mount layer. CHIP_INTERFACE : 'ChipIn... |
| `keysight.ads.de.tech.SmartMountMappingOption` | class | `` | Determines whether or not mount layers are automatically mapped in the SmartMount PCell. Members: AUTOMATIC : 'Automatic': The mapping and alignment is determined automatically. NO_MAPPING : 'NoMapping': Mount layers ... |
| `keysight.ads.de.tech.SmartMountMappingOption.AUTOMATIC` | SmartMountMappingOption | `` | Determines whether or not mount layers are automatically mapped in the SmartMount PCell. Members: AUTOMATIC : 'Automatic': The mapping and alignment is determined automatically. NO_MAPPING : 'NoMapping': Mount layers ... |
| `keysight.ads.de.tech.SmartMountMappingOption.name` | property | `` | name(self: handle) -> str |
| `keysight.ads.de.tech.SmartMountMappingOption.NO_MAPPING` | SmartMountMappingOption | `` | Determines whether or not mount layers are automatically mapped in the SmartMount PCell. Members: AUTOMATIC : 'Automatic': The mapping and alignment is determined automatically. NO_MAPPING : 'NoMapping': Mount layers ... |
| `keysight.ads.de.tech.SmartMountMappingOption.str` | property | `` |  |
| `keysight.ads.de.tech.SmartMountMappingOption.value` | property | `` |  |
| `keysight.ads.de.tech.SmartMountSettings.alignment_type` | property | `` | The alignment type of the SmartMount pcell. This is only applicable if the mapping_option is set to SmartMountMappingOption.NO_MAPPING. |
| `keysight.ads.de.tech.SmartMountSettings.mapping_option` | property | `` | Specify mapping and alignment for the SmartMount pcell. |
| `keysight.ads.de.tech.SmartMountSubtype` | class | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.SmartMountSubtype.BOTTOM_MOUNT` | SmartMountSubtype | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.SmartMountSubtype.CUSTOM` | SmartMountSubtype | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.SmartMountSubtype.FLIP_CHIP` | SmartMountSubtype | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.SmartMountSubtype.MULTI_MOUNT` | SmartMountSubtype | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.SmartMountSubtype.NONE` | SmartMountSubtype | `` | Defines the subtype of a SmartMount PCell. Members: NONE : 'None': No subtype. BOTTOM_MOUNT : 'BottomMount': The bottom metal layers of the chip are mapped to the mount layer on the module. FLIP_CHIP : 'FlipChip': The... |
| `keysight.ads.de.tech.Tech` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a technology database for a library. This Tech can reference (i.e. inherit) the technology from other libraries. |
| `keysight.ads.de.tech.Tech.actual_interop_type` | property | `` | The effective interoperability type determined by settings in this tech and inherited tech. |
| `keysight.ads.de.tech.Tech.all_layers` | property | `` | Return the complete collection of layers in this Tech database. The collection also includes Layers from referenced technology. |
| `keysight.ads.de.tech.Tech.all_purposes` | property | `` | Return the complete collection of Purposes in this Tech database. The collection also includes Purposes from referenced technology. |
| `keysight.ads.de.tech.Tech.create_derived_layer_boolean` | function | `(self, layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, layer2: keysight.ads.de.tech._tech.Layer \| str) -> keysight.ads.de.tech._tech.DerivedLayer` | Create a derived layer from two source layers and boolean operation. The derived layer contains all the shapes that result by performing the boolean operation on all the shapes from the two source layers. |
| `keysight.ads.de.tech.Tech.create_derived_layer_sizing` | function | `(self, layer_name: str, layer_num: int, operation: keysight.ads.de._pde.tech.LayerOp \| str, layer1: keysight.ads.de.tech._tech.Layer \| str, distance: int) -> keysight.ads.de.tech._tech.DerivedLayer` | Create a derived layer from a single source layer, a sizing operation, and a distance parameter. The derived layer contains all the shapes that result by performing the sizing operation on all the shapes from the sour... |
| `keysight.ads.de.tech.Tech.create_physical_layer` | function | `(self, layer_name: str, layer_num: int) -> keysight.ads.de.tech._tech.PhysicalLayer` |  |
| `keysight.ads.de.tech.Tech.dbu_per_uu_sch` | property | `` | The ratio of database units to user units in schematic and symbol views. |
| `keysight.ads.de.tech.Tech.delete_all_layers` | function | `(self) -> None` |  |
| `keysight.ads.de.tech.Tech.delete_layer` | function | `(self, layer: Union[str, int, keysight.ads.de.tech._tech.Layer]) -> None` |  |
| `keysight.ads.de.tech.Tech.find_layer` | function | `(self, layer: Union[int, str], local: bool = False) -> Optional[keysight.ads.de.tech._tech.Layer]` |  |
| `keysight.ads.de.tech.Tech.interop_type` | property | `` | The interoperability type defined in this tech only. If this technology does not have resolution defined, this will be InteropType.UNSPECIFIED. To get the interoperability type determined by inherited tech, use actual... |
| `keysight.ads.de.tech.Tech.layer` | function | `(self, layer: Union[int, str], local: bool = False) -> keysight.ads.de.tech._tech.Layer` |  |
| `keysight.ads.de.tech.Tech.layer_maps` | property | `` | Return the collection of layer maps in this Tech database. |
| `keysight.ads.de.tech.Tech.layer_names` | function | `(self, local: bool = False) -> list[str]` | Get the names of all the physical layers. |
| `keysight.ads.de.tech.Tech.layer_numbers` | function | `(self, local: bool = False) -> list[int]` | Get the numbers of all the physical layers. |
| `keysight.ads.de.tech.Tech.layers` | property | `` | Return the collection of layers in this Tech database. The collection only includes Layers defined in this tech. |
| `keysight.ads.de.tech.Tech.referenced_lib_names` | property | `` | The names of the libraries directly referenced by this Tech. |
| `keysight.ads.de.tech.Tech.save_layer_maps` | function | `(self) -> None` | Save the layer maps to this Tech's library. |
| `keysight.ads.de.tech.Tech.user_units_sch` | property | `` | The name of the user units used in schematic and symbol views. |

### `keysight.ads.emtools`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.emtools.create_empro_view` | function | `(empro_lcv: tuple[str, str, str], tool: str, layout_lcv: tuple[str, str, str], substrate_ls: tuple[str, str]) -> None` | Create a view, saved on disk, that can be opened in the specified EM tool. Parameters ---------- empro_lcv Tuple containing the library name, cell name and the EM view name to be created. tool EM tool name, eihter 'pi... |
| `keysight.ads.emtools.create_empro_view_ex` | function | `(empro_lib: str, empro_cell: str, empro_view: str, tool: str, layout_lib: str, layout_cell: str, layout_view: str, substrate_lib: str, substrate: str) -> None` |  |
| `keysight.ads.emtools.create_emproview` | function | `(empro_lcv: tuple, tool: str, layout_lcv: tuple, substrate_ls: tuple) -> None` | create_emproview is deprecated, and will be removed in the 2026 Update 1 release. Use create_empro_view instead. |
| `keysight.ads.emtools.create_emproview_ex` | function | `(empro_lib: str, empro_cell: str, empro_view: str, tool: str, layout_lib: str, layout_cell: str, layout_view: str, substrate_lib: str, substrate: str) -> None` | create_emproview_ex is deprecated, and will be removed in the 2026 Update 1 release. Use create_empro_view_ex instead. |
| `keysight.ads.emtools.deprecated` | function | `(version: str, message: Optional[str] = None)` | Mark a function or class as deprecated. :param version: release version in which the feature will be *removed*. :param message: additional deprecation message. |
| `keysight.ads.emtools.DesignRef` | class | `` |  |
| `keysight.ads.emtools.DesignRef.layout` | property | `` |  |
| `keysight.ads.emtools.DesignRef.layout_switch_list` | property | `` |  |
| `keysight.ads.emtools.DesignRef.set_layout` | instancemethod | `` | set_layout(self: keysight.ads.emtools._emtools.DesignRef, arg0: str, arg1: str, arg2: str) -> None |
| `keysight.ads.emtools.DesignRef.set_substrate` | instancemethod | `` | set_substrate(self: keysight.ads.emtools._emtools.DesignRef, arg0: str, arg1: str) -> None |
| `keysight.ads.emtools.DesignRef.substrate` | property | `` |  |
| `keysight.ads.emtools.Dict` | _SpecialGenericAlias | `(*args, **kwargs)` | A generic version of dict. |
| `keysight.ads.emtools.EmproSetup` | class | `(filepath__or__empro_lcv_tuple: str \| tuple \| None = None) -> 'EmproSetup'` | Class to work on the EM view setup. |
| `keysight.ads.emtools.EmproSetup.default_filename` | function | `(self) -> str` | Returns the default EM view setup file name. |
| `keysight.ads.emtools.EmproSetup.design_refs` | property | `` | The design references -- layout and substrate -- of the EM view setup. :getter: Returns this setup's design references. :setter: Sets this setup's design references. |
| `keysight.ads.emtools.EmproSetup.tool` | property | `` | The tool for this EM view setup. :getter: Returns this setup's tool. :setter: Sets this setup's tool. |
| `keysight.ads.emtools.EmproSetup.write` | function | `(self, filepath_or_lcv: str \| tuple) -> None` | Writes the EM view setup data. Parameters ---------- filepath_or_lcv Either provide a tuple of strings -- library name, cell name and view name -- or provide the view's setup filepath. |
| `keysight.ads.emtools.find_emsetup_view_name` | function | `(layout_lcv: tuple[str, str, str]) -> str` | Find the active EM Setup view name from the Layout view. Parameters ---------- layout_lcv Tuple containing the library name, cell name and the layout view name. Returns ------- The EM Setup view name Raises ------ Run... |
| `keysight.ads.emtools.get_substrate_info` | function | `(emsetup_lcv: tuple[str, str, str]) -> tuple[str, str]` | Get the substrate info of the EM Setup view. Parameters ---------- emsetup_lcv Tuple containing the library name, cell name and the EM Setup view name. Returns ------- Tuple containing the substrate library name and t... |
| `keysight.ads.emtools.update_empro_view` | function | `(empro_lcv: tuple[str, str, str]) -> None` | Update the EM view after a layout or substrate change. Updates the auxiliary files associated with the EM view: .adsPcells cache, adsMultiTechData.json, proj.ltd,... Parameters ---------- empro_lcv Tuple containing th... |
| `keysight.ads.emtools.version` | function | `() -> str` | Returns the version of the emtools package. |
| `keysight.ads.emtools.version_number` | function | `() -> int` |  |

### `keysight.edatoolbox.ads`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.ads.ADS.create_workspace` | function | `(self, location: str, workspace_name: str, include_system_libraries: bool = True)` | Create a workspace with given name at the given location. Parameters ---------- location : str Parent folder of the new workspace. workspace_name : str Name of the new workspace. include_system_libraries : bool, defau... |
| `keysight.edatoolbox.ads.ADS.import_brd` | function | `(self, workspace: str, brdFile: str)` | Import a brd file into an existing workspace. Parameters ---------- workspace : str Path to an existing workspace. brdFile : str Path to a brd file. Raises ------ AssertionError Workspace does not exist. RuntimeError ... |
| `keysight.edatoolbox.ads.ADS.import_ipc2581` | function | `(self, workspace: str, ipc2581_file: str, library: str, cell: str)` | Import an IPC-2581 file into an existing workspace. Requires ADS 2025 or later. Parameters ---------- workspace : str Path to an existing workspace. ipc2581_file : str Path to an IPC-2581 document. library : str Libra... |
| `keysight.edatoolbox.ads.ADS.import_odbpp` | function | `(self, workspace: str, tgzFile: str, library: str, cell: str = None, use_legacy_importer=True, import_options=None)` | Import an ODB++ file into an existing workspace. Parameters ---------- workspace : str Path to an existing workspace. tgzFile : str Path to an ODB++ archive. library : str Library base name. By default, the new ODB++ ... |
| `keysight.edatoolbox.ads.dataclass` | function | `(cls=None, /, *, init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False, weakref_slot=False)` | Add dunder methods based on the fields defined in the class. Examines PEP 526 __annotations__ to determine fields. If init is true, an __init__() method is added to the class. If repr is true, a __repr__() method is a... |
| `keysight.edatoolbox.ads.errno` | module | `` | This module makes available standard errno system symbols. The value of each symbol is the corresponding integer value, e.g., on most systems, errno.ENOENT equals the integer 2. The dictionary errno.errorcode maps num... |
| `keysight.edatoolbox.ads.ErrorCodes` | class | `(*values)` | Enum where members are also (and must be) ints |
| `keysight.edatoolbox.ads.ErrorCodes.as_integer_ratio` | method_descriptor | `(self, /)` | Return a pair of integers, whose ratio is equal to the original int. The ratio is in lowest terms and has a positive denominator. >>> (10).as_integer_ratio() (10, 1) >>> (-10).as_integer_ratio() (-10, 1) >>> (0).as_in... |
| `keysight.edatoolbox.ads.ErrorCodes.denominator` | getset_descriptor | `` | the denominator of a rational number in lowest terms |
| `keysight.edatoolbox.ads.ErrorCodes.from_bytes` | builtin | `(bytes, byteorder='big', *, signed=False)` | Return the integer represented by the given array of bytes. bytes Holds the array of bytes to convert. The argument must either support the buffer protocol or be an iterable object producing bytes. Bytes and bytearray... |
| `keysight.edatoolbox.ads.ErrorCodes.numerator` | getset_descriptor | `` | the numerator of a rational number in lowest terms |
| `keysight.edatoolbox.ads.IntEnum` | class | `(new_class_name, /, names, *, module=None, qualname=None, type=None, start=1, boundary=None)` | Enum where members are also (and must be) ints |
| `keysight.edatoolbox.ads.IntEnum.as_integer_ratio` | method_descriptor | `(self, /)` | Return a pair of integers, whose ratio is equal to the original int. The ratio is in lowest terms and has a positive denominator. >>> (10).as_integer_ratio() (10, 1) >>> (-10).as_integer_ratio() (-10, 1) >>> (0).as_in... |
| `keysight.edatoolbox.ads.IntEnum.denominator` | getset_descriptor | `` | the denominator of a rational number in lowest terms |
| `keysight.edatoolbox.ads.IntEnum.from_bytes` | builtin | `(bytes, byteorder='big', *, signed=False)` | Return the integer represented by the given array of bytes. bytes Holds the array of bytes to convert. The argument must either support the buffer protocol or be an iterable object producing bytes. Bytes and bytearray... |
| `keysight.edatoolbox.ads.IntEnum.numerator` | getset_descriptor | `` | the numerator of a rational number in lowest terms |
| `keysight.edatoolbox.ads.logging` | module | `` | Logging package for Python. Based on PEP 282 and comments thereto in comp.lang.python. Copyright (C) 2001-2022 Vinay Sajip. All Rights Reserved. To use, simply 'import logging' and log away! |
| `keysight.edatoolbox.ads.MaterialDatabase.semi_conductors` | property | `` |  |
| `keysight.edatoolbox.ads.OdbImportOptions` | class | `(layout_resolution: int = None) -> None` | Options for importing ODB++ files into the EDA toolbox. Attributes ---------- add_new_components_to_existing_library : bool If True, add new components to an existing component library. component_cell_names : OdbImpor... |
| `keysight.edatoolbox.ads.OdbImportOptions.add_new_components_to_existing_library` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.CellName` | class | `(*values)` | Enumeration of cell name options for the ODB++ import. Attributes ---------- LEGACY : int Create component cell names as in the legacy ODB++ importer. PART_NAME : int Set component cell names to corresponding part nam... |
| `keysight.edatoolbox.ads.OdbImportOptions.component_cell_names` | CellName | `` | Enumeration of cell name options for the ODB++ import. Attributes ---------- LEGACY : int Create component cell names as in the legacy ODB++ importer. PART_NAME : int Set component cell names to corresponding part nam... |
| `keysight.edatoolbox.ads.OdbImportOptions.component_library_name` | str | `` | str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str Create a new string object from the given object. If encoding or errors is specified, then the object must expose a data buffer that will be deco... |
| `keysight.edatoolbox.ads.OdbImportOptions.create_new_design_library` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.layer_mapping_file_path` | str | `` | str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str Create a new string object from the given object. If encoding or errors is specified, then the object must expose a data buffer that will be deco... |
| `keysight.edatoolbox.ads.OdbImportOptions.link_line_segments` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.lower_case_cell_names` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.mask_as_dielectric_layer` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.process_negative_artwork` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.separate_component_lib` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.separate_tech_lib` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.skip_design_import` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.skip_non_substrate_layer` | bool | `` | Returns True when the argument is true, False otherwise. The builtins True and False are the only two instances of the class bool. The class bool is a subclass of the class int, and cannot be subclassed. |
| `keysight.edatoolbox.ads.OdbImportOptions.step_index` | int | `` | int([x]) -> integer int(x, base=10) -> integer Convert a number or string to an integer, or return 0 if no arguments are given. If x is a number, return x.__int__(). For floating-point numbers, this truncates towards ... |
| `keysight.edatoolbox.ads.OdbImportOptions.tech_library_name` | str | `` | str(object='') -> str str(bytes_or_buffer[, encoding[, errors]]) -> str Create a new string object from the given object. If encoding or errors is specified, then the object must expose a data buffer that will be deco... |
| `keysight.edatoolbox.ads.os` | module | `` | OS routines for NT or Posix depending on what system we're on. This exports: - all functions from posix or nt, e.g. unlink, stat, etc. - os.path is either posixpath or ntpath - os.name is either 'posix' or 'nt' - os.c... |
| `keysight.edatoolbox.ads.Path` | class | `(*args, **kwargs)` | PurePath subclass that can make system calls. Path represents a filesystem path but unlike PurePath, also offers methods to do system calls on path objects. Depending on your system, instantiating a Path will return e... |
| `keysight.edatoolbox.ads.Path.absolute` | function | `(self)` | Return an absolute version of this path No normalization or symlink resolution is performed. Use resolve() to resolve symlinks and remove '..' segments. |
| `keysight.edatoolbox.ads.Path.is_reserved` | function | `(self)` | Return True if the path contains one of the special names reserved by the system, if any. |
| `keysight.edatoolbox.ads.Path.match` | function | `(self, path_pattern, *, case_sensitive=None)` | Return True if this path matches the given pattern. If the pattern is relative, matching is done from the right; otherwise, the entire path is matched. The recursive wildcard '**' is *not* supported by this method. |
| `keysight.edatoolbox.ads.Path.parser` | module | `` | Common pathname manipulations, WindowsNT/95 version. Instead of importing this module directly, import os and refer to this module as os.path. |
| `keysight.edatoolbox.ads.Path.parts` | property | `` | An object providing sequence-like access to the components in the filesystem path. |
| `keysight.edatoolbox.ads.Path.rmdir` | function | `(self)` | Remove this directory. The directory must be empty. |
| `keysight.edatoolbox.ads.Path.stat` | function | `(self, *, follow_symlinks=True)` | Return the result of the stat() system call on this path, like os.stat() does. |
| `keysight.edatoolbox.ads.Path.stem` | property | `` | The final path component, minus its last suffix. |
| `keysight.edatoolbox.ads.Path.unlink` | function | `(self, missing_ok=False)` | Remove this file or link. If the path is a directory, use rmdir() instead. |
| `keysight.edatoolbox.ads.Path.with_stem` | function | `(self, stem)` | Return a new path with the stem changed. |
| `keysight.edatoolbox.ads.Path.with_suffix` | function | `(self, suffix)` | Return a new path with the file suffix changed. If the path has no suffix, add given suffix. If the given suffix is an empty string, remove the suffix from the path. |
| `keysight.edatoolbox.ads.re` | module | `` | Support for regular expressions (RE). This module provides regular expression matching operations similar to those found in Perl. It supports both 8-bit and Unicode strings; both the pattern and the strings being proc... |
| `keysight.edatoolbox.ads.stat` | module | `` | Constants/functions for interpreting results of os.stat() and os.lstat(). Suggested usage: from stat import * |
| `keysight.edatoolbox.ads.SubstrateLayer` | class | `(materialname: str, toprough: str, thick: float, thickunit: str, precedence: int, angle: float, layer: int, negative: int, index: int, subtype: int, bottomrough: str, processRole: int, pinsOnly: int, expand: int, sheet: int) -> None` | SubstrateLayer(materialname: str, toprough: str, thick: float, thickunit: str, precedence: int, angle: float, layer: int, negative: int, index: int, subtype: int, bottomrough: str, processRole: int, pinsOnly: int, exp... |
| `keysight.edatoolbox.ads.SubstrateMaterial` | class | `(index: int, materialname: str, thick: float, thickunit: str, BAL_NUM: int, BAL_TYPE: str) -> None` | SubstrateMaterial(index: int, materialname: str, thick: float, thickunit: str, BAL_NUM: int, BAL_TYPE: str) |
| `keysight.edatoolbox.ads.SubstrateModel` | class | `(tech_subst_file_name=None)` |  |
| `keysight.edatoolbox.ads.SubstrateModel.layers` | property | `` |  |
| `keysight.edatoolbox.ads.SubstrateModel.materials` | property | `` |  |
| `keysight.edatoolbox.ads.SubstrateModel.read` | function | `(self, file_name)` |  |
| `keysight.edatoolbox.ads.SubstrateModel.write` | function | `(self, file_name=None)` |  |
| `keysight.edatoolbox.ads.SubstrateVia` | class | `(processRole: int, platingenabled: int, index1: int, index2: int, materialname: str, subtype: int, rough: str, layer: int, platingdielectricmaterial: str, platingthickness: float, platingthicknessunit: str, precedence: int) -> None` | SubstrateVia(processRole: int, platingenabled: int, index1: int, index2: int, materialname: str, subtype: int, rough: str, layer: int, platingdielectricmaterial: str, platingthickness: float, platingthicknessunit: str... |
| `keysight.edatoolbox.ads.tempfile` | module | `` | Temporary files. This module provides generic, low- and high-level interfaces for creating temporary files and directories. All of the interfaces provided by this module can be used without fear of race conditions exc... |
| `keysight.edatoolbox.ads.tmpdir` | function | `()` | Context manager to create a temporary directory. Similar to tempfile.TemporaryDirectory, but uses safe_rmtree to deal with intermittent access errors. |
| `keysight.edatoolbox.ads.tmpfile` | function | `(suffix: str = '', prefix: str = 'dat', dir: Optional[str] = None, text: bool = False)` | Context manager to create a temporary file. Only the file path is returned, not the file object. The file is automatically deleted on scope exit. Parameters ---------- suffix : str, default="" The temporary file name ... |
| `keysight.edatoolbox.ads.try_int_float` | function | `(x)` | Attempt to convert the given argument to either an integer or a float. If the argument can be converted to an integer, the function returns the integer value. If the argument cannot be converted to an integer but can ... |
| `keysight.edatoolbox.ads.warnings` | module | `` | Python part of the warnings subsystem. |
| `keysight.edatoolbox.ads.xml` | module | `` | Core XML support for Python. This package contains four sub-packages: dom -- The W3C Document Object Model. This supports DOM Level 1 + Namespaces. parsers -- Python wrappers for XML parsers (currently only supports E... |

### `keysight.edatoolbox.xxpro`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.xxpro.get_python_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the python installed with xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.get_xxpro_location` | function | `(from_ads=True) -> str` | Returns the location of the latest installed xxPro. Parameters ---------- from_ads : bool, default=True If True get xxPro from ADS install folder, otherwise look for EMPROHOME environment variable. |
| `keysight.edatoolbox.xxpro.load_pro_view` | function | `(xxpro_lcv: keysight.edatoolbox.ads.LibraryCellView)` | Load an xxpro LibraryCellView into the empro.activeProject. Parameters ---------- xxpro_lcv : LibraryCellView An xxpro LibraryCellView object. Raises ------ ImportError Failed to import empro module. |
| `keysight.edatoolbox.xxpro.os` | module | `` | OS routines for NT or Posix depending on what system we're on. This exports: - all functions from posix or nt, e.g. unlink, stat, etc. - os.path is either posixpath or ntpath - os.name is either 'posix' or 'nt' - os.c... |
| `keysight.edatoolbox.xxpro.re` | module | `` | Support for regular expressions (RE). This module provides regular expression matching operations similar to those found in Perl. It supports both 8-bit and Unicode strings; both the pattern and the strings being proc... |
