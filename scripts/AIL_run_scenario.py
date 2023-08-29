import calliope
year = str(2050)
case = 'A'
pop = 'h'
cli = 'rcp8'
version = "noCO2"
model_name ='model_'+ year + '_' + case
scenario = pop+'_'+cli+'_'+case+'_'+year

#WITHOUT VERSION
# name_yaml = year + '/' + model_name + '.yaml'
# name_nc = model_name+'_'+pop+'_'+cli+'.nc'
# name_csv = model_name+'_'+pop+'_'+cli +'.csv'

#WITH VERSION
name_yaml = year + '/' + model_name +'_'+version+ '.yaml'
name_nc = model_name+'_'+pop+'_'+cli+'_'+ version +'.nc'
name_csv = model_name+'_'+pop+'_'+cli+'_'+ version +'.csv'

model = calliope.Model(name_yaml, scenario = scenario)
calliope.set_log_verbosity('INFO') #sets the level of verbosity of Calliope's operations
model.run()
model.to_netcdf('results/'+name_nc)
model.to_csv('results/'+name_csv)