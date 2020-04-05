# Notes and Comments

## Comments / Questions on the paper

#### Migration from one age group to another
Given the time scale of the epidemic (months), can this be simplify and assume the number of the people in each age category remains constant.

The system of ODEs will therefore become:

![\begin{aligned}& \dot{S}_{gsa} = & -\lambda(t)_{gsa}S_{gsa} + \frac{(P_{gsa}+N_{gsa})}{DI_g} &\\& \dot{I}_{gsa} = & \lambda(t)_{gsa}S_{gsa} - (\frac{1}{WIP_g} + \frac{1}{DAI_g})I_{gsa} &\\& \dot{G}_{gsa} = & \frac{I_{gsa}}{WIP_g} - \frac{G_{gsa}}{DWT_g} &\\& \dot{P}_{gsa} = & PSC_g(\frac{I_{gsa}}{DAI_g} + \frac{G_{gsa}}{DWT_g}) - \frac{P_{gsa}}{DI_g} & \\ & \dot{N}_{gsa} = & (1-PSC_g)(\frac{I_{gsa}}{DAI_g} + \frac{G_{gsa}}{DWT_g}) - \frac{N_{gsa}}{DI_g} & \\\end{aligned}](https://render.githubusercontent.com/render/math?math=%5Cbegin%7Baligned%7D%26%20%5Cdot%7BS%7D_%7Bgsa%7D%20%3D%20%26%20-%5Clambda(t)_%7Bgsa%7DS_%7Bgsa%7D%20%2B%20%5Cfrac%7B(P_%7Bgsa%7D%2BN_%7Bgsa%7D)%7D%7BDI_g%7D%20%26%5C%5C%26%20%5Cdot%7BI%7D_%7Bgsa%7D%20%3D%20%26%20%5Clambda(t)_%7Bgsa%7DS_%7Bgsa%7D%20-%20(%5Cfrac%7B1%7D%7BWIP_g%7D%20%2B%20%5Cfrac%7B1%7D%7BDAI_g%7D)I_%7Bgsa%7D%20%26%5C%5C%26%20%5Cdot%7BG%7D_%7Bgsa%7D%20%3D%20%26%20%5Cfrac%7BI_%7Bgsa%7D%7D%7BWIP_g%7D%20-%20%5Cfrac%7BG_%7Bgsa%7D%7D%7BDWT_g%7D%20%26%5C%5C%26%20%5Cdot%7BP%7D_%7Bgsa%7D%20%3D%20%26%20PSC_g(%5Cfrac%7BI_%7Bgsa%7D%7D%7BDAI_g%7D%20%2B%20%5Cfrac%7BG_%7Bgsa%7D%7D%7BDWT_g%7D)%20-%20%5Cfrac%7BP_%7Bgsa%7D%7D%7BDI_g%7D%20%26%20%5C%5C%20%26%20%5Cdot%7BN%7D_%7Bgsa%7D%20%3D%20%26%20(1-PSC_g)(%5Cfrac%7BI_%7Bgsa%7D%7D%7BDAI_g%7D%20%2B%20%5Cfrac%7BG_%7Bgsa%7D%7D%7BDWT_g%7D)%20-%20%5Cfrac%7BN_%7Bgsa%7D%7D%7BDI_g%7D%20%26%20%5C%5C%5Cend%7Baligned%7D)


#### Model parameters
The model has the following parameters:
- ![DI_g: \text{the duration of immunity}](https://render.githubusercontent.com/render/math?math=DI_g%3A%20%5Ctext%7Bthe%20duration%20of%20immunity%7D)
- ![WIP_g: \text{the incubation period}](https://render.githubusercontent.com/render/math?math=WIP_g%3A%20%5Ctext%7Bthe%20incubation%20period%7D)
- ![DAI_g: \text{the duration of asymptomatic infectious symptoms}](https://render.githubusercontent.com/render/math?math=DAI_g%3A%20%5Ctext%7Bthe%20duration%20of%20asymptomatic%20infectious%20symptoms%7D)
- ![DWT_g: \text{the duration of the treatment}](https://render.githubusercontent.com/render/math?math=DWT_g%3A%20%5Ctext%7Bthe%20duration%20of%20the%20treatment%7D)
- ![PSC_g: \text{the probability of becoming seropositive}](https://render.githubusercontent.com/render/math?math=PSC_g%3A%20%5Ctext%7Bthe%20probability%20of%20becoming%20seropositive%7D)

As can be seen the parameters are gender specific. Given the data available for Covid-19, age specific parameter might be more appropriate.


#### Deceased State
In the current model the state *P* (seropositive) is equivalent to the recovered state. The state *N* represents the seronegative case. If we wanted to introduce the deceased state we could use the *N* state and remove the connection between *N* and *S*.


#### Social Mixing matrix
The matrix should allow gender mixing as well. The size of the matrix is therefore (2 x 2 x 4 x 4 x 20 x 20)