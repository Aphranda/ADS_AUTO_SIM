# ADS Python API Probe

Generated: 2026-08-03T00:04:59
Python: `D:\Hardware\Keysight\ADS2026_Update1\tools\python\python.exe`
Keywords: `port, emport, secondary, gndlayer, gnd, reference`

## API Hits

### `keysight.ads.de`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.CellviewRef.cell` | property | `` | The referenced cell. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.cell_name` | property | `` | The name of the referenced cell. Read-only. Might be empty if not specified. |
| `keysight.ads.de.CellviewRef.lib` | property | `` | The referenced library. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.lib_name` | property | `` | The name of the referenced library. Read-only. Might be empty if not specified. |
| `keysight.ads.de.CellviewRef.view` | property | `` | The referenced view. Read-only. Might be ``None`` if not specified. |
| `keysight.ads.de.CellviewRef.view_name` | property | `` | The name of the referenced view. Read-only. Might be empty if not specified. |
| `keysight.ads.de.find_inst_in_associated_schematic` | function | `(inst_name: str, design: 'Design') -> tuple['Instance', 'Design']` | Find the named instance in the associated schematic of the given design. Typically used to find the substrate or process block referenced by parameters of layout instances. The value returned is a tuple containing the... |
| `keysight.ads.de.find_inst_in_schematic_hierarchy` | function | `(inst_name: str, hierarchy: 'DesignHierarchy') -> tuple['Instance', 'Design']` | Search up the hierarchy to find the named instance in the associated schematics of the designs in the hierarchy. Typically used to find the substrate or process block referenced by parameters of layout instances. The ... |
| `keysight.ads.de.get_cell_module` | function | `(lib_name: str, cell_name: str) -> module` | Import the Python module for an OpenAccess cell. |
| `keysight.ads.de.get_library_module` | function | `(lib_name: str) -> module` | Import the Python module for an OpenAccess library. |
| `keysight.ads.de.get_path_for_use_in_library_definition_file` | function | `(path: pathlib._local.Path \| str, lib_def_file_path: pathlib._local.Path \| str) -> str` | Convert a path to a simplified path for use in a library definition file. The simplified path may be relative to the library definition file path or may contain environment variable references of the form $VAR/path. |
| `keysight.ads.de.get_smart_package_module` | function | `(package_name: str) -> module` | Import the Python module for an ADS Smart Package. |
| `keysight.ads.de.get_view_module` | function | `(lib_name: str, cell_name: str, view_name: str) -> module` | Import the Python module for an OpenAccess cellview. |
| `keysight.ads.de.LibDefList` | class | `()` | Represents a library definition file. The current implementation supports only short term usage. The members are a snapshot of the members at the time the LibDefList was created. |
| `keysight.ads.de.Library.get_layout_preference` | function | `(self, index: 'LibSpecificPreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.get_library_cfg_var` | function | `(self, pref_name: str) -> str` | Get a variable from the library configuration file. If the value contains environment variable references, those values will be substituted. |
| `keysight.ads.de.Library.get_schematic_preference` | function | `(self, index: 'LibSpecificPreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.set_layout_preference` | function | `(self, index: 'LibSpecificPreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Library.set_schematic_preference` | function | `(self, index: 'LibSpecificPreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.LineItem.name` | property | `` | Name of this line type definition. References to line items by layout objects use this name. |
| `keysight.ads.de.PrinterOrientation` | class | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.PrinterOrientation.LANDSCAPE` | PrinterOrientation | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.PrinterOrientation.PORTRAIT` | PrinterOrientation | `` | Members: PORTRAIT LANDSCAPE |
| `keysight.ads.de.Tech` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | Represents a technology database for a library. This Tech can reference (i.e. inherit) the technology from other libraries. |
| `keysight.ads.de.Tech.all_layers` | property | `` | Return the complete collection of layers in this Tech database. The collection also includes Layers from referenced technology. |
| `keysight.ads.de.Tech.all_purposes` | property | `` | Return the complete collection of Purposes in this Tech database. The collection also includes Purposes from referenced technology. |
| `keysight.ads.de.Tech.referenced_lib_names` | property | `` | The names of the libraries directly referenced by this Tech. |
| `keysight.ads.de.Workspace.get_layout_preference` | function | `(self, index: 'WorkspacePreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.get_schematic_preference` | function | `(self, index: 'WorkspacePreference') -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.set_layout_preference` | function | `(self, index: 'WorkspacePreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.Workspace.set_schematic_preference` | function | `(self, index: 'WorkspacePreference', value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |

### `keysight.ads.de.db_uu`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.de.db_uu.ApolloObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AppObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Arc.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ArrayInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ArrayInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ArrayInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ArrayInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.AttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.AttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.BlockObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BundleTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BundleTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusNetBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.BusTermBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.BusTermBit.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.BusTermBit.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.CompositeObject.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CompoundForm` | class | `(name: str, label: str = '', params: collections.abc.Sequence[keysight.ads.de.db._model_def.ModelParam] = [], net_format: str = '', display_format: str = '', dialog_data: str = '') -> None` | CompoundForm is a type of Form for a parameter that contains one or more sub-parameters. The CompoundForm describes how the parameter is netlisted and displayed. The Form for each sub-parameter describes how that port... |
| `keysight.ads.de.db_uu.ConstructionLine.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CustomVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.CustomVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.CustomVia.via_master_lcv_name` | property | `` | The cellview name of the master design referenced by this custom via. |
| `keysight.ads.de.db_uu.Design.get_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')]) -> 'PreferenceValueType'` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Design.set_preference` | function | `(self, preference: Union[ForwardRef('WorkspacePreference'), ForwardRef('LibSpecificPreference')], value: 'PreferenceValueType') -> None` | Use ``with de.experimental.preferences():`` to work with preferences. The API is subject to change. |
| `keysight.ads.de.db_uu.Donut.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Donut.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Dot.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Dot.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ellipse.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ellipse.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.EMBoundaryWalls.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EvalText.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.EvalText.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Fig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Fig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroup.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.FigGroup.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.FigGroupMem.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Group.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.GroupMember.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.GroupMember.object` | property | `` | The object associated with this member. This may be None if the group contains objects that are not supported by ADS. |
| `keysight.ads.de.db_uu.Instance.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Instance.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.Instance.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.Instance.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Instance.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.InstAttrDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstAttrDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstPropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.InstPropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.InstTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Interconnect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Interconnect.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Interconnect. |
| `keysight.ads.de.db_uu.Keepout.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Line.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Line.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Line.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Line. |
| `keysight.ads.de.db_uu.MomentumMesh.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Net.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Param.evaluate_no_expr` | function | `(self) -> str` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.Param.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamBase.evaluate_no_expr` | function | `(self) -> Union[str, list[str], list[list[str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamBase.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]], list[list[Union[bool, int, float, str]]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_no_expr` | function | `(self) -> list[str]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamCompound.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str]]` | Prepare this compound parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_no_expr` | function | `(self) -> Union[str, list[str]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables... |
| `keysight.ads.de.db_uu.ParamNonRepeated.evaluate_without_expr` | function | `(self) -> Union[bool, int, float, str, list[Union[bool, int, float, str]]]` | Prepare this parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or variables. |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_no_expr` | function | `(self) -> Union[list[str], list[list[str]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.ParamRepeated.evaluate_without_expr` | function | `(self) -> list[typing.Union[bool, int, float, str, list[typing.Union[bool, int, float, str]]]]` | Prepare this repeated parameter value for use by removing quotes and evaluating units. Does not support expressions. Will raise an exception if the value has an arithmetic expression or references other parameters or ... |
| `keysight.ads.de.db_uu.Path.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Path.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Path.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Path. |
| `keysight.ads.de.db_uu.PathSeg.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PathSeg.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBBase.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBBase.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBPad.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBPad.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBPad.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBPad.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.PCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.PCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.PCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.PCellInfo.reference_name` | property | `` | The reference name for reference PCells. |
| `keysight.ads.de.db_uu.PCellInfo.supports_psn_behavior` | property | `` | True if the PCell supports PSN behavior. |
| `keysight.ads.de.db_uu.PCellInfo.supports_scaling` | property | `` | True if the PCell supports scaling. |
| `keysight.ads.de.db_uu.PCellType.REFERENCE` | PCellType | `` | Defines the type of a PCell. Members: NONE : 'None': Not a PCell. AEL_MACRO : 'AELMacro': The PCell generator uses an AEL Macro function. PSN : 'PSN': The PCell generator uses a parameterized sub-network design. GENER... |
| `keysight.ads.de.db_uu.Pin.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Pin.update_pin_annotation` | function | `(self, annot_data: Optional[ForwardRef('PinAnnotData')] = None, *, preserve_origin: bool = True) -> None` | Update the pin annotation. If annot_data is None, the design preferences will be used. If preserve_origin is True, the annotation origin will not be moved. |
| `keysight.ads.de.db_uu.PinFig.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PinFig.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Plane.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Polygon.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Polygon.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Polygon.interconnect_info` | property | `` | Return a reference to the cached copy of the InterconnectInfo for this Polygon. |
| `keysight.ads.de.db_uu.PropDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.PropDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Rect.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Rect.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Ref.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Ref.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.RefIter` | class | `(design: 'Design') -> None` | An iterator for Refs (Instance or Via references) in a Design. |
| `keysight.ads.de.db_uu.ScalarInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.ScalarInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.ScalarInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.ScalarInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.ScalarNet.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarTerm.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.ScalarTerm.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.ScalarTerm.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo` | class | `(term_name: str, is_positive: bool)` | Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.is_positive` | property | `` | True if this term is a positive term. This is used to determine the polarity of the term in EMPorts. |
| `keysight.ads.de.db_uu.SecondaryTermInfo.term_name` | property | `` | The name of the secondary term. |
| `keysight.ads.de.db_uu.Shape.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Shape.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StackedPCBVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.StackedPCBVia.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.StackedPCBVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.StackedPCBVia.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.StdVia.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.StdVia.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.Term.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Term.is_delta_gap_port` | property | `` | True if this term is a delta gap port. |
| `keysight.ads.de.db_uu.Term.secondary_term_info` | property | `` | A copy of the list of secondary term information for this term. Secondary terms are used to represent related terms that are used in EMPorts. |
| `keysight.ads.de.db_uu.Text.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Text.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextBase.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextBase.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextDisplay.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextDisplay.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.TextOverride` | class | `(unused: keysight.ads.de._utils.InvalidCall, *args, **kwargs) -> None` | A text object that supports overriding text from an instance master. |
| `keysight.ads.de.db_uu.TextOverride.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.TextOverride.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInst.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInst.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInst.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInst.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.VectorInstBit.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_cell` | property | `` | The cell of the effective instance master. In most cases, this will be the same as the actual master cell. But when using smart mount, this will be the referenced master cell. |
| `keysight.ads.de.db_uu.VectorInstBit.effective_master_lcv_name` | property | `` | The LCVName of the effective instance master. In most cases, this will be the same as the actual master name. But when using smart mount, this will be the referenced master name. |
| `keysight.ads.de.db_uu.VectorInstBit.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |
| `keysight.ads.de.db_uu.VectorInstBit.get_referenced_design_name` | function | `(self) -> str` | Return the referenced design name if this is a pcell instance that references a design. |
| `keysight.ads.de.db_uu.Via.delete_object` | function | `(self) -> None` | Delete this object from its design. Use this with care. It is generally ok to delete top level objects, but if other objects reference this object there may be alternative APIs. |
| `keysight.ads.de.db_uu.Via.fig_group_mem` | property | `` | Return the FigGroupMem that references this Fig, if it is a member of a FigGroup. |

### `keysight.ads.emtools`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.ads.emtools.EmproSetup.design_refs` | property | `` | The design references -- layout and substrate -- of the EM view setup. :getter: Returns this setup's design references. :setter: Sets this setup's design references. |

### `keysight.edatoolbox.xxpro`

| Object | Kind | Signature | Doc |
|---|---|---|---|
| `keysight.edatoolbox.xxpro.load_pro_view` | function | `(xxpro_lcv: keysight.edatoolbox.ads.LibraryCellView)` | Load an xxpro LibraryCellView into the empro.activeProject. Parameters ---------- xxpro_lcv : LibraryCellView An xxpro LibraryCellView object. Raises ------ ImportError Failed to import empro module. |
| `keysight.edatoolbox.xxpro.os` | module | `` | OS routines for NT or Posix depending on what system we're on. This exports: - all functions from posix or nt, e.g. unlink, stat, etc. - os.path is either posixpath or ntpath - os.name is either 'posix' or 'nt' - os.c... |
| `keysight.edatoolbox.xxpro.re` | module | `` | Support for regular expressions (RE). This module provides regular expression matching operations similar to those found in Perl. It supports both 8-bit and Unicode strings; both the pattern and the strings being proc... |
