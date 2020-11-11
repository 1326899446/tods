import os
import sklearn
import numpy
import typing
import time
from scipy import sparse
from numpy import ndarray
from collections import OrderedDict
from typing import Any, Callable, List, Dict, Union, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import logging, uuid
from scipy import sparse
from numpy import ndarray
from collections import OrderedDict

from d3m import container
from d3m.exceptions import PrimitiveNotFittedError
from d3m.container import DataFrame as d3m_dataframe
from d3m.container.numpy import ndarray as d3m_ndarray
from d3m.primitive_interfaces import base, transformer
from d3m.metadata import base as metadata_base, hyperparams
from d3m.metadata import hyperparams, params, base as metadata_base
from d3m.primitive_interfaces.base import CallResult, DockerContainer

from statsmodels.tsa.stattools import acf


# import os.path


__all__ = ('ColumnFilterPrimitive',)

Inputs = container.DataFrame
Outputs = container.DataFrame



class Hyperparams(hyperparams.Hyperparams):

	# Keep previous
	dataframe_resource = hyperparams.Hyperparameter[typing.Union[str, None]](
		default=None,
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="Resource ID of a DataFrame to extract if there are multiple tabular resources inside a Dataset and none is a dataset entry point.",
	)
	use_columns = hyperparams.Set(
		elements=hyperparams.Hyperparameter[int](-1),
		default=(2,),
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="A set of column indices to force primitive to operate on. If any specified column cannot be parsed, it is skipped.",
	)
	exclude_columns = hyperparams.Set(
		elements=hyperparams.Hyperparameter[int](-1),
		default=(0,1,3,),
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="A set of column indices to not operate on. Applicable only if \"use_columns\" is not provided.",
	)
	return_result = hyperparams.Enumeration(
		values=['append', 'replace', 'new'],
		default='append',
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="Should parsed columns be appended, should they replace original columns, or should only parsed columns be returned? This hyperparam is ignored if use_semantic_types is set to false.",
	)
	use_semantic_types = hyperparams.UniformBool(
		default=False,
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="Controls whether semantic_types metadata will be used for filtering columns in input dataframe. Setting this to false makes the code ignore return_result and will produce only the output dataframe"
	)
	add_index_columns = hyperparams.UniformBool(
		default=False,
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="Also include primary index columns if input data has them. Applicable only if \"return_result\" is set to \"new\".",
	)
	error_on_no_input = hyperparams.UniformBool(
		default=True,
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
		description="Throw an exception if no input column is selected/provided. Defaults to true to behave like sklearn. To prevent pipelines from breaking set this to False.",
	)
	return_semantic_type = hyperparams.Enumeration[str](
		values=['https://metadata.datadrivendiscovery.org/types/Attribute',
			'https://metadata.datadrivendiscovery.org/types/ConstructedAttribute'],
		default='https://metadata.datadrivendiscovery.org/types/Attribute',
		description='Decides what semantic type to attach to generated attributes',
		semantic_types=['https://metadata.datadrivendiscovery.org/types/ControlParameter']
	)



class ColumnFilterPrimitive(transformer.TransformerPrimitiveBase[Inputs, Outputs, Hyperparams]):
	"""
	A primitive that filters out columns of wrong shape in DataFrame (specifically columns generated by some features analysis)
	"""

	metadata = metadata_base.PrimitiveMetadata({
		'__author__': "DATA Lab @Texas A&M University",
		'name': "Column Filter",
		'python_path': 'd3m.primitives.tods.data_processing.column_filter',
		'source': {'name': "DATALAB @Taxes A&M University", 'contact': 'mailto:khlai037@tamu.edu',
				   'uris': ['https://gitlab.com/lhenry15/tods/-/blob/Yile/tods/tods/data_processing/column_filter.py']},
		'algorithm_types': [metadata_base.PrimitiveAlgorithmType.COLUMN_FILTER,], 
		'primitive_family': metadata_base.PrimitiveFamily.DATA_PREPROCESSING,
		'id': str(uuid.uuid3(uuid.NAMESPACE_DNS, 'ColumnFilterPrimitive')),
		'version': '0.0.1',		
		})


	def __init__(self, *, hyperparams: Hyperparams) -> None:
	 	super().__init__(hyperparams=hyperparams)

	 	#self._clf = column_filter()


	def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:	
		"""
		Process the testing data.
		Args:
			inputs: Container DataFrame.

		Returns:
			Container DataFrame after AutoCorrelation.
		"""
		outputs=inputs
		index_to_keep = np.array([])

		for i in range(len(inputs.columns)):
			column_to_check = outputs.iloc[:,i]
			cell_to_check = column_to_check.iloc[-1:]

			if not np.isnan(cell_to_check.values[0]):
				index_to_keep=np.append(index_to_keep,i)

		outputs=outputs.iloc[:,index_to_keep]		

		self._update_metadata(outputs)

		return CallResult(outputs)




	def _update_metadata(self, outputs):
		outputs.metadata = outputs.metadata.generate(outputs)
 
	
