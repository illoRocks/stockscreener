<?php 

$income = array(
                    'Umsatzerloese' => array(
                                        'NoninterestIncome', 
                                        'InterestAndDividendIncomeOperating', 
                                        'Revenues',
                                        'SalesRevenueGoodsNet',
                                        'SalesRevenueNet'),
                    'Materialaufwand' => array(
                                        'CostOfGoodsSold',
                                        'CostOfRevenue', 
                                        'CostOfGoodsAndServicesSold',
                                        'CostOfPurchasedOilAndGas',
                                        'FoodAndPaperCosts',
                                        'CrudeOilAndProductPurchases',
                                        'CostOfServicesExcludingDepreciationDepletionAndAmortization',
                                        'CostOfGoodsSoldExcludingDepreciationDepletionAndAmortization',
                                        ),
                    'Verwaltungsaufwand' => array(
                                        'GeneralAndAdministrativeExpense', 
                                        'SellingGeneralAndAdministrativeExpense'),
                    'FundEKosten' => array(
                                        'ResearchAndDevelopmentExpense'),
                    'EBIT' => array(
                                        'OperatingIncomeLoss'),
                    'Finanzaufwendungen' => array(
                                        'InterestAndDebtExpense', 
                                        'InterestExpenseExcludingFinancialProducts'),
                    'EBT' => array(
                                        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments', 
                                        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'), #change to EBIT
                    'Steueraufwand' => array(
                                        'IncomeTaxExpenseBenefit'),
                    'Jahresueberschuss' => array(
                                        'NetIncomeLoss', 
                                        'ProfitLoss')
                );
$balance = array(
                    'ForderungenLuL' => array(
                                        'AccountsReceivableNetCurrent', 
                                        'AccountsNotesAndLoansReceivableNetCurrent', 
                                        'ReceivablesNetCurrent'),
                    'Bilanzsumme' => array(
                                        'Assets', 
                                        'LiabilitiesAndStockholdersEquity'),
                    'Umlaufvermoegen' => array('AssetsCurrent'),
                    'liquideMittel' => array('CashAndCashEquivalentsAtCarryingValue', 
                                        'CashCashEquivalentsAndFederalFundsSold', 
                                        'CashCashEquivalentsAndShortTermInvestments', 
                                        'CashAndEquivalentsExcludingAssetsHeldForSale',
                                        'CarryingValueOfCashAndCashEquivalents'),
                    'Wertpapiere' => array(
                                        'MarketableSecuritiesCurrent', 
                                        'AvailableForSaleSecuritiesCurrent', 
                                        'AvailableForSaleSecuritiesEquitySecurities'),
                    'Vorraete' => array('InventoryNet',
                                        'InventoryFinishedGoodsAndWorkInProcess',
                                        'InventoryPartsAndComponentsNetOfReserves', 
                                        'InventoryNetOfCustomerAdvancesAndProgressBillings', 
                                        'InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings'),
                    'Goodwill'           => array('Goodwill'),
                    'kurzKapitalanlagen' => array('ShortTermInvestments'),
                    'VerbindlichkeitenLuL' => array(
                                        'AccountsPayableCurrent',
                                        'AccountsPayableAndAccruedLiabilitiesCurrent'),
                    'kurzVerbindlichkeiten' => array(
                                        'LiabilitiesCurrent'),
                    'kurzfrFinanzverbindlichkeiten' => array(
                                        'ShortTermBorrowings',
                                        'LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths', 
                                        'DebtCurrent',
                                        'LongTermDebtCurrent',
                                        'CommercialPaper'),
                    'langfrFinanzverbindlichkeiten' => array(
                                        'LongTermDebtAndCapitalLeaseObligations', 
                                        'LongTermDebtNoncurrent',
                                        'LongTermDebt'),
                    'MinderheitenAnteile' => array(
                                        'MinorityInterest'),
                    'Eigenkapital' => array(
                                        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
                                        'StockholdersEquity')
                );
$cashflow = array(
                    'Abschreibungen' => array(
                                        'Depreciation', 
                                        'AmortizationOfIntangibleAssets', 
                                        'AmortizationOfFinancingCostsAndDiscounts', 
                                        'DepreciationDepletionAndAmortization',
                                        'DepreciationAmortizationAndOtherNoncashItems',
                                        'DepreciationAndAmortization',
                                        'DepreciationAmortizationAndOther',
                                        'DepreciationAmortizationAndAccretionNet',
                                        'DepreciationAndAmortizationExcludingDeferredPolicyAcquisitionCostAmortizationExpense'),
                    'OperativerCashflow' => array(
                                        'NetCashProvidedByUsedInOperatingActivities', 
                                        'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations'),
                    'ErwerbVonSachanlagen' => array( 
                                        'PaymentsToAcquireProductiveAssets',
                                        'PaymentsToAcquirePropertyPlantAndEquipment',
                                        'PaymentsToAcquireInvestments'),
                    'CashflowausFinanzierungstätigkeit' => array(
                                        'NetCashProvidedByUsedInInvestingActivities', 
                                        'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations')
                );
$info = array(
                    'TradingSymbol',
                    'DocumentPeriodEndDate',
                    'DocumentType',
                    'EntityRegistrantName',
                    'EntityCentralIndexKey',
                    'SIC',
                    'CurrentFiscalYearEndDate'
                );


function cut_label($value)
{
  switch ($value) {
    case 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments': return 'EBT';break;
    case 'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest': return 'EBT';break;
    case 'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest': return 'StockholdersEquityIncludingNoncontrollingInterest';break;
    case 'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations': return 'NetCashProvidedByUsedInOperatingActivities';break;
    case 'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations': return 'NetCashProvidedByUsedInInvestingActivitiesCO';break;
    case 'InventoryNetOfAllowancesCustomerAdvancesAndProgressBillings': return 'InventoryNetOfCustomerAdvancesAndProgressBillings';break;
    case 'LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths': return 'LongTermDebtRepaymentsInNextTwelveMonths';break;
    case 'DepreciationAndAmortizationExcludingDeferredPolicyAcquisitionCostAmortizationExpense': return 'DepreciationAndAmortization';break;
    default: return $value; break;
  }
}
?>