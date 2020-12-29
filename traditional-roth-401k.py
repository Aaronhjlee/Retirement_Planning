'''
Last updated 2020-12-28
'''

import pandas as pd
import numpy as np

class profit():
    def __init__(self):
        pass

    def roth_401k(self, years, annual_contribution, percent_return):
        res = annual_contribution
        annual_list =[annual_contribution]
        for i in range(years):
            res = annual_contribution + annual_list[i] * percent_return
            annual_list.append(int(res))
        return annual_list

    def traditional_401k_post_tax(self, df, tax_low):
        # input dataframe with 401k_roth column
        
        res=[]
        for i in df['401k_roth']:
            res.append(int(i*tax_low))
        return res

    def tax_bracket(self, base_salary, annual_contribution):
        # if no tax bracket change, then go with roth 100% -- if bracket changes, put as much in traditional to lower tax bracket
    
        bracket_list = [9875, 40125, 85525, 163300, 207350, 518400]
        tax_list = [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]
        diff = base_salary - annual_contribution

        if diff > bracket_list[5]:
            traditional_contribution = 0
            roth_contribution = annual_contribution
        else:
            for i in range(4, 0, -1):
                if bracket_list[i] < diff <= bracket_list[i+1]:
                    if base_salary - bracket_list[i+1] < 0:
                        tax_up = tax_list[i+1]
                        tax_low = tax_list[i]
                        traditional_contribution = 0
                        roth_contribution = annual_contribution
                        print('Your tax bracket is: {}%'.format(tax_up))
                        print('Contribute ${} to your traditional 401k'.format(traditional_contribution))
                        print('You should contribute {} to your roth 401k at your current tax rate of {}%'.format(roth_contribution, tax_up))
                    else:
                        tax_up = tax_list[i+2]
                        tax_low = tax_list[i+1]
                        traditional_contribution = base_salary - bracket_list[i+1]
                        roth_contribution = annual_contribution - (base_salary - bracket_list[i+1])
                        print('Your upper tax is: {}%'.format(tax_up))
                        print('Your lower tax is: {}%'.format(tax_low))
                        print('You can lower your tax bracket to {}% by contributing to your traditional 401k: ${}'.format(tax_low, traditional_contribution))
                        print('Contribute the rest to your roth 401k: ${}'.format(roth_contribution))
        
        trad = round(traditional_contribution / 24, 2)
        roth = round(roth_contribution / 24, 2)
        print('-------------------------------------------------------------------------------------')
        print('Bimonthly traditional 401k contribution: {}'.format(trad))
        print('Bimonthly roth 401k contribution: {}'.format(roth))

        return (1-tax_up), (1-tax_low)
        

    def brokerage_list(self, years, annual_contribution, percent_return_non_401k, base_salary, tax_up, tax_low):
        roth = base_salary*tax_up - annual_contribution
        traditional = (base_salary-annual_contribution)*tax_low  
        difference = traditional - roth
        
        annual_trad_list =[difference]
        for i in range(years):
            res = difference + annual_trad_list[i] * percent_return_non_401k
            annual_trad_list.append(int(res))
        return annual_trad_list


    def brokerage_post_tax(self, df):
        long_term_capital_gains_tax=0.2
        res=[]
        for i in df['lost roth 401k oppurtunity_cost']:
            res.append(int(i*(1-long_term_capital_gains_tax)))
        return res


    '''
    --------------------------------------------------------------------------------------------------
    '''

    def howdy_401k(self, age, retirement_age, annual_contribution, percent_return, percent_return_non_401k, base_salary):
        print('Your base salary is {}'.format(base_salary))
        years = retirement_age-age
        
        # make the table
        df = pd.DataFrame(list(range(years+1)), columns=['years'])
        
        # find tax range
        tax_up, tax_low = self.tax_bracket(base_salary, annual_contribution)

        # create the return for 401k
        df['401k_roth'] = self.roth_401k(years, annual_contribution, percent_return)
        df['401k_traditional (pre_tax)'] = self.roth_401k(years, annual_contribution, percent_return)
        
        # create the return post tax traditional
        df['401k_traditional (post_tax)'] = self.traditional_401k_post_tax(df, tax_low)
        
        # create brokerage by getting the difference and capturing oppurtunity cost
        brokerage = self.brokerage_list(years, annual_contribution, percent_return, base_salary, tax_up, tax_low)
        df['lost roth 401k oppurtunity_cost'] = brokerage    
        
        # create brokerage returns post tax
        df['lost roth 401k oppurtunity_cost (capital_gain_tax)'] = self.brokerage_post_tax(df)
        
        df['difference (trad<>roth)'] = df['401k_roth'] - (df['401k_traditional (post_tax)']+df['lost roth 401k oppurtunity_cost (capital_gain_tax)'])
        
        return df

mod = profit()
df = mod.howdy_401k(age=30, retirement_age=65, annual_contribution=19000, percent_return=1.075, percent_return_non_401k=1.08, base_salary=100000)
df