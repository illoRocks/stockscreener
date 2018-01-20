<?php 

$map = array(
			// if + take sum
			'income' => array(
	
				'Revenues' => 'revenueTotal',
				'SalesRevenueGoodsNet' => 'revenueTotal',
				'SalesRevenueNet' => 'revenueTotal',

			// costOfRevenue
				
				'CostOfRevenue'  => 'costOfRevenue',
				'CostOfGoodsAndServicesSold'  => 'costOfRevenue',
				'CostOfGoodsSoldAndOtherOperatingCharges'  => 'costOfRevenue',
				'CrudeOilAndProductPurchases'  => 'costOfRevenue',
				// 'PolicyholderBenefitsAndClaimsIncurredHealthCare'  => 'costOfRevenue', -> 731766??
				// sum of
				'CostOfGoodsSold'  => 'costOfRevenue+',
				'CostOfServices'  => 'costOfRevenue+',
				// sum of
				'CostOfPurchasedOilAndGas'  => 'costOfRevenue+',
				'OperatingCostsAndExpenses'  => 'costOfRevenue+',
				
				// sum
				'FoodAndPaperCosts'  => 'costOfRevenue+',
				'PayrollAndEmployeeBenefits'  => 'costOfRevenue+',
				'OccupancyAndOtherOperatingExpenses'  => 'costOfRevenue+',
				'FranchiseCosts' => 'costOfRevenue+',
				'CompanyOperatedRestaurantExpenses'  => 'costOfRevenue+',

				// sum of
				'CostOfServicesExcludingDepreciationDepletionAndAmortization'  => 'costOfRevenue+',
				'CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization'  => 'costOfRevenue+',

			// profitGross
				'GrossProfit'  => 'profitGross',

			// researchAndDevelopment
				'ResearchAndDevelopmentExpense' => 'researchAndDevelopment',
				'ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost' => 'researchAndDevelopment',
				'ResearchAndDevelopmentCostsIncludingSoftwareDevelopmentCosts' => 'researchAndDevelopment',

			// sellingGeneralAndAdministrative
				'SellingGeneralAndAdministrativeExpense' => 'sellingGeneralAndAdministrative',

				// sum of
				'GeneralAndAdministrativeExpense' => 'sellingGeneralAndAdministrative+',
				'SellingAndMarketingExpense' => 'sellingGeneralAndAdministrative+',

			// nonRecurring
				'RestructuringAndRelatedCostIncurredCost' => 'nonRecurring',
				'ImpairmentIntegrationAndRestructuringExpenses' => 'nonRecurring',
				'RestructuringChargesAndAcquisitionRelatedCosts' => 'nonRecurring',
				'ExplorationExpense' => 'nonRecurring',
				'RestructuringCharges' => 'nonRecurring',

			// operatingExpensesOther
				'CostAndExpensesOther' => 'operatingExpensesOther',
				'OtherCostAndExpenseOperating' => 'operatingExpensesOther',
				
				// sum of
				'TaxesOtherThanOnIncome' => 'operatingExpensesOther+',
				'DepreciationDepletionAndAmortization' => 'operatingExpensesOther+',
				'OtherOperatingIncomeExpenseNet' => 'operatingExpensesOther+',
				'GoodwillImpairmentLoss' => 'operatingExpensesOther+',
				'AmortizationOfIntangibleAssetsNotAssociatedWithSingleFunction' => 'operatingExpensesOther+',
				'UnusualOrInfrequentItemOperating' => 'operatingExpensesOther+',
				'AmortizationOfIntangibleAssets' => 'operatingExpensesOther+',

			// operatingExpensesTotal
				'CostsAndExpenses' => 'operatingExpensesTotal',


			// operatingIncome
				'OperatingIncomeLoss' => 'operatingIncome',

			//nonOperatingIncomeNetOther
				'CostsExpensesAndOther' => 'nonOperatingIncomeNetOther',
				'OtherNonoperatingIncomeExpense' => 'nonOperatingIncomeNetOther',

			//incomeBeforeInterestAndTax

			//interestExpense
				'InterestExpense' => 'interestExpense',
				'InterestExpenseDebt' => 'interestExpense',
				'InterestAndOtherFinancialCharges' => 'interestExpense',


			//incomeBeforeTax
				'IncomeLossFromContinuingOperationsBeforeIncomeTaxes' => 'incomeBeforeTax',
				'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments' => 'incomeBeforeTax',
				'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest' => 'incomeBeforeTax',

			//incomeTaxExpense
				'IncomeTaxExpenseBenefit' => 'incomeTaxExpense',


			//minorityInterest
				'NetIncomeLossAttributableToNoncontrollingInterest' => 'minorityInterest',


			//incomeNetFromContinuingOps
				'IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest' => 'incomeNetFromContinuingOps',


			//discontinuedOps
				'IncomeLossFromDiscontinuedOperationsNetOfTax' => 'discontinuedOps',


			//extraordinaryItems


			//incomeNet
				'NetIncomeLoss' => 'incomeNet',
				'ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest' => 'incomeNet',
						
				),

			'balance' => array(

			// commonStockSharesOutstanding
				'EntityCommonStockSharesOutstanding' => 'commonStockSharesOutstanding',

			//cashAndCashEquivalents
				'CashAndCashEquivalentsAtCarryingValue' => 'cashAndCashEquivalents',
				'CarryingValueOfCashAndCashEquivalents' => 'cashAndCashEquivalents',

			//shortTermInvestments
				'MarketableSecuritiesCurrent' => 'shortTermInvestments',
				'AvailableForSaleSecuritiesCurrent' => 'shortTermInvestments',
				'ShortTermInvestments' => 'shortTermInvestments',
			
			//cashAndShortTermInvestments
				'CashCashEquivalentsAndShortTermInvestments' => 'cashAndShortTermInvestments',
			
			//receivablesNet
				'AccountsNotesAndLoansReceivableNetCurrent' => 'receivablesNet',
				'AccountsReceivableNetCurrent' => 'receivablesNet',
				'ReceivablesNetCurrent' => 'receivablesNet',
			
			//inventory
				'InventoryNet' => 'inventory',
				'InventoryFinishedGoodsNetOfReserves' => 'inventory',
			
			//currentAssetsOther
				'PrepaidExpenseAndOtherAssetsCurrent' => 'currentAssetsOther',
				'OtherAssetsCurrent' => 'currentAssetsOther',
				'CurrentDeferredTaxAssetsAndOtherAssetsCurrent' => 'currentAssetsOther',
				'PrepaidExpenseCurrent' => 'currentAssetsOther',
			
			//currentAssetsTotal
				'AssetsCurrent' => 'currentAssetsTotal',
			
			//longTermInvestments
				'InvestmentsInAffiliatesSubsidiariesAssociatesAndJointVentures' => 'longTermInvestments',
				'MarketableSecuritiesNoncurrent' => 'longTermInvestments',
				'LongTermInvestments' => 'longTermInvestments',
				'SelectedFinancialAssetsLongTermInvestmentsAndLoans' => 'longTermInvestments',
				'EquityMethodInvestments' => 'longTermInvestments',
			
			//propertyPlantAndEquipmentGross
				'PropertyPlantAndEquipmentGross' => 'propertyPlantAndEquipmentGross',
			
			//accumulatedDepreciation
				'AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment' => 'accumulatedDepreciation',
			
			//propertyPlantAndEquipmentNet
				'PropertyPlantAndEquipmentNet' => 'propertyPlantAndEquipmentNet',
				
			//goodwill
				'Goodwill' => 'goodwill',
			
			//intangibleAssets
				'IntangibleAssetsNetExcludingGoodwill' => 'intangibleAssets',
				'OtherIndefiniteLivedAndFiniteLivedIntangibleAssets' => 'intangibleAssets',

				// sum of
				'DeferredTaxAssetsOther' => 'intangibleAssets+',
				'FiniteLivedIntangibleAssetsNet' => 'intangibleAssets+',
			
			//nonCurrrentAssetsOther
				'Miscellaneous' => 'nonCurrrentAssetsOther',
				'DeferredIncomeTaxesAndOtherAssetsNoncurrent' => 'nonCurrrentAssetsOther',
				'OtherAssetsNoncurrent' => 'nonCurrrentAssetsOther',
			
			//nonCurrentAssetsTotal
			
			//assetsTotal
				'Assets' => 'assetsTotal',
			
			//accountsPayable
				'AccountsPayableCurrent' => 'accountsPayable',
				'AccountsPayableAndAccruedLiabilitiesCurrent' => 'accountsPayable',
			
			//shortTermDebt
				'DebtCurrent' => 'shortTermDebt',
				'ShortTermBorrowings' => 'shortTermDebt',
				'ConvertibleDebtCurrent' => 'shortTermDebt',
				'LongTermDebtCurrent' => 'shortTermDebt',
			
			//currentLiabilitiesOther
				'OtherLiabilitiesCurrent' => 'currentLiabilitiesOther',
				'CurrentDeferredTaxLiabilitiesAndOtherCurrentLiabilities' => 'currentLiabilitiesOther',
				'LiabilitiesHeldForSaleAtCarryingValue' => 'currentLiabilitiesOther',

			
			//currentLiabilitiesTotal
				'LiabilitiesCurrent' => 'currentLiabilitiesTotal',
			
			//longTermDebtTotal
				'LongTermDebt' => 'longTermDebtTotal',
				'LongTermDebtNoncurrent' => 'longTermDebtTotal+',

			// capitalLeaseObligationsNoncurrent
				'CapitalLeaseObligationsNoncurrent' => 'capitalLeaseObligationsNoncurrent',


			// LongTermDebtAndCapitalLeaseObligations
				'LongTermDebtAndCapitalLeaseObligations' => 'longTermDebtAndCapitalLeaseObligations',

			
			//nonCurrentLiabilitiesOtherAndDefferedIncomeTax  errechenbar = nonCurrentLiabilitiesTotal - longTermDebtTotal
			
			//nonCurrentLiabilitiesTotal
			
			//minorityInterest
				'MinorityInterest' => 'minorityInterest',
			
			//negativeGoodwill
			
			//liabilitiesTotal
			
			//warrants
			
			//stockholderEquityTotal
				'StockholdersEquity' => 'stockholderEquityTotal',
			// equityTotal
				'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest' => 'equityTotal',
				
			
			//liabilitiesAndStockholdersEquity
				'LiabilitiesAndStockholdersEquity' => 'liabilitiesAndStockholdersEquity'

			),
			'cashflow' => array(

			//netIncome
					'NetIncomeLoss' => 'netIncome',

			//depreciation
				'DepreciationAndAmortization' => 'depreciation',
				'DepreciationDepletionAndAmortization' => 'depreciation',
				'DepreciationAmortizationAndOther' => 'depreciation',
				'DepreciationDepletionAndAmortizationIncludingDiscontinuedOperationDepreciationandAmortization' => 'depreciation',
				'DepreciationDepletionAndAmortizationincludingdiscontinuedoperations' => 'depreciation',
				
				// sum of
				'Depreciation' => 'depreciation+',
				'AmortizationAndOther' => 'depreciation+',
				'AmortizationOfIntangibleAssets' => 'depreciation+',

			//changeReceivables
				'IncreaseDecreaseInReceivables' => 'changeReceivables',
				'IncreaseDecreaseInAccountsReceivable' => 'changeReceivables',
				'IncreaseDecreaseInAccountsAndNotesReceivable' => 'changeReceivables',

			//changeLiabilitiesAndAccountsPayable
				'IncreaseDecreaseInAccountsPayableAndOtherOperatingLiabilities' => 'changeLiabilitiesAndAccountsPayable',
				'IncreaseDecreaseInAccountsPayableAndAccruedLiabilities' => 'changeLiabilitiesAndAccountsPayable',
				// sum of
				'IncreaseDecreaseInOtherCurrentLiabilities' => 'changeLiabilitiesAndAccountsPayable+',
				'IncreaseDecreaseInOtherNoncurrentLiabilities' => 'changeLiabilitiesAndAccountsPayable+',
				'IncreaseDecreaseInAccountsPayableTrade' => 'changeLiabilitiesAndAccountsPayable+',
				'IncreaseDecreaseInOtherOperatingLiabilities' => 'changeLiabilitiesAndAccountsPayable+',
				
			//changeInventories
				'IncreaseDecreaseInInventoriesPrepaidExpensesAndOtherCurrentAssets' => 'changeInventories',
				'IncreaseDecreaseInInventories' => 'changeInventories',


			//cashFlowsOtherOperating

			//cashFlowsTotalOperating
				'NetCashProvidedByUsedInOperatingActivities' => 'cashFlowsTotalOperating',
				'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations' => 'cashFlowsTotalOperating',


			//paymentsToAcquirePropertyPlantAndEquipment CapitalExpenditures
				'PaymentsToAcquirePropertyPlantAndEquipment' => 'paymentsToAcquirePropertyPlantAndEquipment',
				'PaymentsToAcquireProductiveAssets' => 'paymentsToAcquirePropertyPlantAndEquipment',

			//proceedsFromSaleOfPropertyPlantAndEquipment CapitalExpenditures
				'ProceedsFromSaleOfPropertyPlantAndEquipment' => 'proceedsFromSaleOfPropertyPlantAndEquipment',
				'ProceedsFromSaleOfProductiveAssets' => 'proceedsFromSaleOfPropertyPlantAndEquipment',


			//paymentsToAcquireInvestments investments
				'PaymentsToAcquireMarketableSecurities' => 'paymentsToAcquireInvestments',
				'PaymentsToAcquireInvestments' => 'paymentsToAcquireInvestments',
				'PaymentsForProceedsFromOtherInvestingActivities' => 'paymentsToAcquireInvestments',

				// sum of
				'PaymentsToAcquireShortTermInvestments' => 'paymentsToAcquireInvestments+',
				

			//proceedsFromSaleOfInvestments

				// sum of
				'ProceedsFromSaleOfShortTermInvestments' => 'proceedsFromSaleOfInvestments+',
				'ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities' => 'proceedsFromSaleOfInvestments+',
				'ProceedsFromSaleOfAvailableForSaleSecurities' => 'proceedsFromSaleOfInvestments+',
				'ProceedsFromSaleAndMaturityOfMarketableSecurities' => 'proceedsFromSaleOfInvestments+',
				'ProceedsFromDivestitureOfBusinessesAndInterestsInAffiliates' => 'proceedsFromSaleOfInvestments+',

			//cashFlowsOtherInvesting
				'PaymentsForProceedsFromOtherInvestingActivities' => 'cashFlowsOtherInvesting',

			//cashFlowsTotalInvesting
				'NetCashProvidedByUsedInInvestingActivities' => 'cashFlowsTotalInvesting',
				'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations' => 'cashFlowsTotalInvesting',

			//dividends
				'PaymentsOfDividendsCommonStock' => 'dividends',
				'PaymentsOfOrdinaryDividends' => 'dividends',
				'PaymentsOfDividends' => 'dividends',

			// stockSale
				'ProceedsFromStockOptionsExercised' => 'stockSale',
				'StockIssuedDuringPeriodValueNewIssues' => 'stockSalePurchase',
			
			// stockPurchase
				'PaymentsForRepurchaseOfCommonStock' => 'stockPurchase',
			
			//stockSalePurchase
				

			//netBorrowings

			//cashFlowsOtherFinancing

			//cashFlowsTotalFinancing
				'NetCashProvidedByUsedInFinancingActivities' => 'cashFlowsTotalFinancing',
				'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations' => 'cashFlowsTotalFinancing',

			//exchangeRateChanges
				'EffectOfExchangeRateOnCashAndCashEquivalents' => 'exchangeRateChanges',

			//cashAndCashEquivalentsChanges
				'CashAndCashEquivalentsPeriodIncreaseDecrease' => 'cashAndCashEquivalentsChanges'
		)
			);

$report = array(

			'income' => array(

					'revenueTotal',
					'costOfRevenue',
					'profitGross',
					'researchAndDevelopment',
					'sellingGeneralAndAdministrative',
					'nonRecurring',
					'operatingExpensesOther',
					'operatingExpensesTotal',
					'operatingIncome',
					'nonOperatingIncomeNetOther',
					'incomeBeforeInterestAndTaxAndAmortization',
					'incomeBeforeInterestAndTax',
					'interestExpense',
					'incomeBeforeTax',
					'incomeTaxExpense',
					'minorityInterest',
					'incomeNetFromContinuingOps',
					'discontinuedOps',
					'extraordinaryItems',
					'incomeNet',
					
								),

			'balance' => array(


					'cashAndCashEquivalents',
					'shortTermInvestments',
					'cashAndShortTermInvestments',
					'receivablesNet',
					'inventory',
					'currentAssetsOther',
					'currentAssetsTotal',
					'longTermInvestments',
					'propertyPlantAndEquipmentGross',
					'accumulatedDepreciation',
					'propertyPlantAndEquipmentNet',
					'goodwill',
					'intangibleAssets',
					'accumulatedAmortization',
					'nonCurrrentAssetsOther',
										'nonCurrentAssetsTotal',
					'assetsTotal',
					'accountsPayable',
					'shortTermDebt',
					'currentLiabilitiesOther',
					'currentLiabilitiesTotal',
					'longTermDebtTotal',
					// 'nonCurrentLiabilitiesOtherAndDefferedIncomeTax',
					'deferredLongTermLiabilityCharges',
					'nonCurrentLiabilitiesTotal',
					'minorityInterest',
					'negativeGoodwill',
					'liabilitiesTotal',
					'warrants',
					'stockholderEquityTotal',
					'liabilitiesAndStockholdersEquity',
					),

			'cashflow' => array(

					'netIncome',
					'depreciation',
					'changeReceivables',
					'changeLiabilitiesAndAccountsPayable',
					'changeInventories',
					// 'cashFlowsOtherOperating',
					'cashFlowsTotalOperating',
					'paymentsToAcquirePropertyPlantAndEquipment',
					'proceedsFromSaleOfPropertyPlantAndEquipment',
					'capitalExpenditures',
					'paymentsToAcquireInvestments',
					'proceedsFromSaleOfInvestments',
					'investments',
					'cashFlowsOtherInvesting',
					'cashFlowsTotalInvesting',
					'dividends',
					'stockSale',
					'stockPurchase',
					'stockSalePurchase',
					'netBorrowings',
					'cashFlowsOtherFinancing',
					'cashFlowsTotalFinancing',
					'exchangeRateChanges',
					'cashAndCashEquivalentsChanges',
					'freeCashflow'	
					)
			);

$company_info = array(

				'TradingSymbol',
				'EntityCentralIndexKey',
				'EntityRegistrantName',
				'CurrentFiscalYearEndDate'
	);

$needed = array(
				// income
				'revenueTotal',
				'costOfRevenue',
				'sellingGeneralAndAdministrative',
				'operatingExpensesOther',
				'researchAndDevelopment',
				// 'incomeBeforeInterestAndTaxAndAmortization',
				'incomeBeforeInterestAndTax',
				'interestExpense',
				'incomeBeforeTax',
				'incomeTaxExpense',
				'incomeNet',
				// balance
				'cashAndCashEquivalents',
				'shortTermInvestments',
				'receivablesNet',
				'inventory',
				'currentAssetsTotal',
				'goodwill',
				'assetsTotal',
				'accountsPayable',
				'shortTermDebt',
				'currentLiabilitiesTotal',
				'longTermDebtTotal',
				'minorityInterest',
				'stockholderEquityTotal',
				'liabilitiesAndStockholdersEquity',
				// cashflow
				'depreciation',
				'cashFlowsTotalOperating',
				'paymentsToAcquirePropertyPlantAndEquipment',
				'proceedsFromSaleOfPropertyPlantAndEquipment',
				// 'capitalExpenditures',
				'cashFlowsTotalInvesting',
				// 'freeCashflow'
				)
?>