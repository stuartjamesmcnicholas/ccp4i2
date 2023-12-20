# CCP4mg picture definition file
# See http://www.ysbl.york.ac.uk/~ccp4mg/ccp4mg_help/picture_definition.html
# or your local copy of CCP4mg documentation.
# CCP4mg version 2.5.1
# Created Tue Dec 20 10:02:33 2011

view = View (
     orientation = [1.0, 0.0, 0.0, 0.0],
     centre_MolData = '%MOLDATA_XYZOUT%',
     scale = 100.0,
     fog_enabled = 0,
     fog_near = -10.0,
     fog_far = 10.0,
     slab_enabled = False,
     slab_width = 10,
     slab_offset = 0,          )


MolData (
     filename = ['FULLPATH',
                  '%XYZOUT%','%XYZOUT%' ],
     model_symmetry =  { 
                    'symmetry_visible' : [ ],
                    'symmetry_colours' : [ ],
                    'MolDisp_selection' : 'all atoms',
                    'symmetry_MolDisp_objects' : [ ],
                    'MolDisp_visible' : 1  }
      )

MolDisp (
          opacity = 1.0,
          drawing_style = 'model_drawing_styleXYZOUTMolDisp1',
          legend_visible = 0,
          contact_MolDisp = '',
          label_params =  { 
                         'label_style' : [ 
                                        0,
                                        0,
                                        0,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0 ],
                         'label_user_oneperres' : 1,
                         'label_colour' : 'complement',
                         'truncate_mol_name' : 0,
                         'label_user_selparams' :  {  },
                         'label_select' : 'label_no',
                         'truncate_mol_name_length' : 6  },
          selection_parameters =  { 
                         'features' : '',
                         'buried_sel' : '',
                         'property_join' : 'and',
                         'select' : 'all',
                         'ranges_extend' : 1,
                         'nmr_models' : [ ],
                         'ranges_neighb_model' : '',
                         'ranges_neighb_qualifier' : 'all',
                         'neighb_excl_solvent' : 0,
                         'buried_mol' : '',
                         'neighb_hb' : 0,
                         'neighb_sym' : 0,
                         'as_MolDisp' : '',
                         'nothydrogen' : 0,
                         'ranges_qualifier' : '',
                         'monomers' : [ ],
                         'neighb_excl_monomer' : 0,
                         'neighb_sel' : '',
                         'cid' : '',
                         'property_lt_op' : [ ],
                         'neighb_selobj' : '',
                         'neighb_excl' : 1,
                         'buried_and_selection' : '',
                         'property' : [ ],
                         'restypes' : [ ],
                         'symid' : '',
                         'neighb_mol' : '',
                         'ranges_neighb_invert' : 0,
                         'ranges_neighb_cutoff' : 4.0,
                         'property_gt_op' : [ ],
                         'sites' : [ ],
                         'contact_mol' : '',
                         'neighb_rad' : '4.0',
                         'secstr' : [ ],
                         'chains' : [ ],
                         'property_gt_value' : [ ],
                         'alt_locs' : [ ],
                         'contact_sel' : '',
                         'property_lt_value' : [ ],
                         'ranges' : [ ],
                         'atomtype' : '',
                         'selection_scheme' : '',
                         'elementtypes' : [ ],
                         'buried_group' : 'atom',
                         'user_sel' : '',
                         'neighb_group' : 'residue',
                         'ranges_invert' : 0,
                         'ranges_neighb_selection' : ''  },
          colour_parameters =  { 
                         'colour_mode' : 'blend',
                         'colour_legend' : 'Blend through model'  },
          style_parameters =  { 
                         'style_mode' : 'SPLINE'  }          )

MolDisp (
          opacity = 1.0,
          drawing_style = 'model_drawing_styleXYZOUTMolDisp1',
          legend_visible = 0,
          contact_MolDisp = '',
          label_params =  { 
                         'label_style' : [ 
                                        0,
                                        0,
                                        0,
                                        1,
                                        1,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0 ],
                         'label_user_oneperres' : 1,
                         'label_colour' : 'complement',
                         'truncate_mol_name' : 0,
                         'label_user_selparams' :  {  },
                         'label_select' : 'label_no',
                         'truncate_mol_name_length' : 6  },
          selection_parameters =  { 
                         'features' : '',
                         'buried_sel' : '',
                         'property_join' : 'and',
                         'select' : 'side',
                         'ranges_extend' : 1,
                         'nmr_models' : [ ],
                         'ranges_neighb_model' : '',
                         'ranges_neighb_qualifier' : 'all',
                         'neighb_excl_solvent' : 0,
                         'buried_mol' : '',
                         'neighb_hb' : 0,
                         'neighb_sym' : 0,
                         'as_MolDisp' : '',
                         'nothydrogen' : 0,
                         'ranges_qualifier' : '',
                         'monomers' : [ ],
                         'neighb_excl_monomer' : 0,
                         'neighb_sel' : '',
                         'cid' : '',
                         'property_lt_op' : [ ],
                         'neighb_selobj' : '',
                         'neighb_excl' : 1,
                         'buried_and_selection' : '',
                         'property' : [ ],
                         'restypes' : [ ],
                         'symid' : '',
                         'neighb_mol' : '',
                         'ranges_neighb_invert' : 0,
                         'ranges_neighb_cutoff' : 4.0,
                         'property_gt_op' : [ ],
                         'sites' : [ ],
                         'contact_mol' : '',
                         'neighb_rad' : '4.0',
                         'secstr' : [ ],
                         'chains' : [ ],
                         'property_gt_value' : [ ],
                         'alt_locs' : [ ],
                         'contact_sel' : '',
                         'property_lt_value' : [ ],
                         'ranges' : [ ],
                         'atomtype' : 'side',
                         'selection_scheme' : '',
                         'elementtypes' : [ ],
                         'buried_group' : 'atom',
                         'user_sel' : '',
                         'neighb_group' : 'residue',
                         'ranges_invert' : 0,
                         'ranges_neighb_selection' : ''  },
          colour_parameters =  { 
                         'colour_mode' : 'blend',
                         'colour_legend' : 'Blend through model'  },
          style_parameters =  { 
                         'style_mode' : 'FATBONDS'  }          )



ParamsManager( 
          name = 'model_drawing_styleXYZOUTMolDisp1',
          helix_style = 1,
          anisou_scale_byvdw = 1          )

