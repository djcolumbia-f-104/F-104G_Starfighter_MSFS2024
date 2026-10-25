/V"73 -
| NASA  | TECHNICAL  |     | NOTE |     | NASA  TN  | D-7137 |
| ----- | ---------- | --- | ---- | --- | --------- | ------ |
CO
^
| MODELING    |              | OF  AIRPLANE PERFORMANCE |               |                  |     |     |
| ----------- | ------------ | ------------------------ | ------------- | ---------------- | --- | --- |
| FROM        | FLIGHT-TEST  |                          | RESULTS       | AND              |     |     |
| VALIDATION  |              | WITH                     | AN  F-104G    | AIRPLANE         |     |     |
| by  Robert  | T.           | Marshall                 | and  William  | G.  Schweikhard  | }   |     |
| Flight      | Research     | Center                   |               |                  |     |     |
| Edwards,    | Calif.       | 93523                    |               |                  |     |     |
NATIONAL  AERONAUTICS  AND  SPACE  ADMINISTRATION  •  WASHINGTON,  D. C.  •  FEBRUARY 1973

1. Report  No. 2. Government Accession No. 3. Recipient's  Catalog No.
NASA TN D-7137
|     |     |     |     | 5. Report  | Date |     |
| --- | --- | --- | --- | ---------- | ---- | --- |
4. Title and Subtitle
February 1973
MODELING OF AIRPLANE PERFORMANCE FROM FLIGHT-TEST
RESULTS AND VALIDATION WITH AN F-104G AIRPLANE
6. Performing Organization Code
| 7. Author(s)                                  |     |     |     | 8. Performing Organization Report No. |       |     |
| --------------------------------------------- | --- | --- | --- | ------------------------------------- | ----- | --- |
| Robert T. Marshall and William G. Schweikhard |     |     |     |                                       | H-723 |     |
10. Work Unit No.
9. Performing Organization Name and Address
136-13-08-00-24
| NASA Flight Research Center |     |     |     | 11. Contract or Grant No. |     |     |
| --------------------------- | --- | --- | --- | ------------------------- | --- | --- |
P.  O. Box 273
| Edwards, California  | 93523 |     |     |     |     |     |
| -------------------- | ----- | --- | --- | --- | --- | --- |
13. Type of Report and Period Covered
12. Sponsoring Agency Name and Address
Technical Note
National Aeronautics and Space Administration
14. Sponsoring Agency Code
| Washington, D. C.  | 20546 |     |     |     |     |     |
| ------------------ | ----- | --- | --- | --- | --- | --- |
15. Supplementary  Notes
16. Abstract
A technique of defining an accurate performance model of an
airplane from limited flight-test data and predicted aerodynamic
|     | and propulsion system characteristics is developed.  |     |     | With the |     |     |
| --- | ---------------------------------------------------- | --- | --- | -------- | --- | --- |
modeling technique, flight-test data from level accelerations are
used to define a Ig performance model for the entire flight envelope
|     | of an F-104G airplane.  |     | The performance model is defined in terms |     |     |     |
| --- | ----------------------- | --- | ----------------------------------------- | --- | --- | --- |
of the thrust and drag of the airplane and can be varied with changes
|     | in ambient temperature  |     | or airplane weight.  | The model predicts the |     |     |
| --- | ----------------------- | --- | -------------------- | ---------------------- | --- | --- |
performance of the airplane within 5 percent of the measured flight-
|     | test data.  The modeling technique could substantially reduce the |     |     |     |     |     |
| --- | ----------------------------------------------------------------- | --- | --- | --- | --- | --- |
time required for performance flight testing and produce a clear
definition of the thrust and drag characteristics of an airplane.
17. Key Words (Suggested by Author(s)) 18. Distribution Statement
Aircraft performance testing techniques
| Performance modeling |     |     |     | Unclassified |     |     |
| -------------------- | --- | --- | --- | ------------ | --- | --- |
Thrust-drag evaluation
19. Security Classif. (of this report) 20. Security Classif. (of this page) 21. No. of Pages 22. Price*
| Unclassified |                                       | Unclassified |                                             |     | 28    | ,$3.00 |
| ------------ | ------------------------------------- | ------------ | ------------------------------------------- | --- | ----- | ------ |
|              | ' For sale by the National Technical  |              | Information Service, Springfield, Virginia  |     | 22151 |        |

MODELING OF AIRPLANE PERFORMANCE FROM FLIGHT-TEST
RESULTS AND VALIDATION WITH AN F-104G AIRPLANE
Robert T. Marshall and William G. Schweikhard
Flight Research Center
INTRODUCTION
The number of flight tests required to define the performance of"modern aircraft
and the associated costs of the tests are increasing at an alarming rate. Larger flight .
envelopes, the multitude of geometric variables (for example, wing sweep or inlet
geometry, or both), and the variability of external store configurations of modern high
performance aircraft create a matrix of conditions that is nearly impossible to encom-
pass with conventional testing technique's. For this reason, studies are being conducted
by NASA to develop a mathematical performance model from flight-test data so that
the performance for the entire flight envelope of ah aircraft can be determined from a
limited number of flight tests.
An aircraft performance model determined from flight-test data can be defined in
terms of either excess thrust (thrust minus drag) or the specific values of thrust and
drag over the Mach number-altitude operating region. The use of excess thrust data to
define an accurate model is limited in that the individual values of thrust and drag are
not independently known; therefore, excess thrust must be determined for each geometric
configuration and power setting under consideration. Thus many flight tests are neces-
sary to obtain data over the operating envelope of an aircraft. Furthermore, once a
model is defined in terms of excess thrust, it is difficult to adjust it to variations from
standard-day atmospheric conditions, again because the thrust and drag are combined
in one term, making it difficult to separate individual variations of the two parameters.
This problem could be eliminated if a performance model were defined in terms of
absolute values of thrust and drag. The determination of thrust and drag in flight is a
complex, difficult, and tedious process, however, that requires considerably more
flight-test time and instrumentation than the definition of excess thrust.
One way to solve this problem would be to develop a technique of defining a perform-
ance model for the flight envelope of a particular aircraft configuration from limited
flight-test data and the aerodynamic and propulsion system characteristics of the air-
craft. Once defined, such a model could be used to predict the flight performance of the
aircraft at every point in the flight envelope without additional flight testing. If this
could be done, it would reduce the time required for performance flight testing and pro-
duce a clear definition of the thrust and drag characteristics of an aircraft. This report
presents the results of a study made at the NASA Flight Research Center to develop
such a technique. The technique is applied to an F-104G airplane. The measured per-
formance of the airplane is compared with the computed performance of the model.
SYMBOLS
Physical quantities in this report are given in the International System of Units (SI)

and parenthetically  in U. S.  Customary Units.  Measurements were taken in Customary
Units.  Factors relating the two systems  are presented in reference 1.
| C   | drag coefficient,  |     | D/qS |     |
| --- | ------------------ | --- | ---- | --- |
n
| C   | lift coefficient,  | L/qS |     |     |
| --- | ------------------ | ---- | --- | --- |
T _Lj
| D   | total airplane drag,  |         | N (Ib) |     |
| --- | --------------------- | ------- | ------ | --- |
| -F  | net thrust,           | N (Ib)  |        |     |
| FU  | fuel used,            | kg (Ib) |        |     |
2  2
g  acceleration due to gravity,  9. 8 m/sec  (32. 2 ft/sec  )
| g   | mass-to-force  | conversion factor,  |     | 9. 8 N/kg (1 Ibf/lbm) |
| --- | -------------- | ------------------- | --- | --------------------- |
O
| h   | pressure altitude,  |     | m (ft) |     |
| --- | ------------------- | --- | ------ | --- |
V2
| he   | specific energy, h + —                     |     | , m  (ft) |     |
| ---- | ------------------------------------------ | --- | --------- | --- |
| 95-  | rate of change of altitude, m/sec (ft/sec) |     |           |     |
dt
| ^p    | rate of change of specific energy, m/sec (ft/sec) |     |                 |     |
| ----- | ------------------------------------------------- | --- | --------------- | --- |
| Kj-v  | model coefficient                                 |     | for  drag, D^/D |     |
p
K-p  model coefficient  for thrust and fuel flow,  F^/Fp  and
| L   | airplane lift,       | N (Ib) |       |     |
| --- | -------------------- | ------ | ----- | --- |
| M   | Mach number          |        |       |     |
| N   | normal load factor,  |        | L/g W |     |
t/
|     |             | inlet total pressure, N/m2  |     | (lb/in2) |
| --- | ----------- | --------------------------- | --- | -------- |
| p   | compressor  |                             |     |          |
*2
|     | dynamic pressure, N/m2  |     | (lb/ft2) |     |
| --- | ----------------------- | --- | -------- | --- |
q  •
|     |                       |     | f\  o    |     |
| --- | --------------------- | --- | -------- | --- |
| S   | wing reference area,  |     | m^ (ft ) |     |
specific fuel consumption, ks/^ec
| SFC  |                                          |     |         | (   |
| ---- | ---------------------------------------- | --- | ------- | --- |
| T    | total temperature,                       |     | °K (°R) |     |
| T    | ambient temperature at altitude, °K (°R) |     |         |     |
a
2

t
|     | elapsed time,                              | sec     |           |     |
| --- | ------------------------------------------ | ------- | --------- | --- |
| V   | velocity along flight path, m/sec (ft/sec) |         |           |     |
| dV  |                                            | m/sec2  | (ft/sec2) |     |
rate of change of velocity,
dt
| W   | airplane gross weight, kg (Ib) |                 |     |     |
| --- | ------------------------------ | --------------- | --- | --- |
| Wf  | total fuel flow,               | kg/sec (Ib/sec) |     |     |
| a   | angle of attack,               | deg             |     |     |
| y   | flight path angle,             | deg             |     |     |
|     | change in specific             | parameter       |     |     |
Ptc
to
|     | compressor  | inlet total pressure  | ratio,  •" |   3 , |
| --- | ----------- | --------------------- | ---------- | ----- |
  x
thrust deflection angle,  deg
Subscripts:
predicted
P
| s   | standard day |     |     |     |
| --- | ------------ | --- | --- | --- |
| t   | test day     |     |     |     |
PRINCIPLES OF PERFORMANCE  MODELING TECHNIQUES
The term "performance model" is used in
its simplest form in this report to refer to a
mathematical description of the motion of an
aircraft  in the vertical plane as given by
| equations (1) and (2).  | For this discussion the |     |     |     |
| ----------------------- | ----------------------- | --- | --- | --- |
forces were resolved parallel and perpendic-
ular to the flight path, as indicated in the
| adjacent sketch,  and the angle of attack was |     |     |     |     |
| --------------------------------------------- | --- | --- | --- | --- |
assumed to be small.
g WdV
(1)
F - D - g W sin? = —
c
gdt
|     | L - g W cos 7 = g W (N - cos 7) |     | (2) |     |
| --- | ------------------------------- | --- | --- | --- |
C  C

In the development of the performance model, only nonmaneuvering flight (that is,
a normal load factor of 1, constant direction of flight, and constant power setting) was
considered. For a normal load factor near 1, equation (2) becomes a secondary correc-
tion to the model. As shown in references 2 to 4, equation (1) can be rewritten in terms
of the rate of climb, acceleration, and velocity of the airplane as follows:
D v
(V t) t /dh ydv\
g W ~ V d t+ gdty/ (3)
c t t
The right side of this equation can be determined easily by measuring the velocity and
the rates of change of altitude and velocity of an airplane. On the left side of this
"equation, the weight can also be obtained easily; however, thrust and drag cannot be
explicitly defined in flight and are unknowns in the equation. Therefore, a second
equation must be developed which allows either the simultaneous solution of the two
equations or the determination of an explicit value of thrust or drag.
Experience with in-flight thrust measurements on the XB-70 airplane showed that
even though the measured thrust did not usually agree with the predicted thrust, the
predicted specific fuel consumption, SFC , which is the ratio of fuel flow to thrust, was
D
generally accurate. The ratio of the measured to the predicted specific fuel consump-
tion is presented in figure 1 for the XB-70 airplane at maximum power. As indicated
by the dispersion in the data at any given Mach number, the predicted specific fuel con-
sumption is generally within 5 percent of the measured value. On the basis of this
observation, it was assumed that the ratio of the in-flight measured fuel flow to thrust
should be approximately equal to the ratio of the predicted fuel flow to thrust corrected
for the test-day temperature as shown by equations (4) and (5):
I« ' D± fi t * '
where
W = W + AW
f f f
(5)
The values of AWf and AF are obtained from equations (A5) and (A 6) of appendix A. ,
Furthermore, reference 5 indicates that the climb and acceleration performance of an
aircraft Is fairly insensitive to nominal errors in specific fuel consumption. In refer-
ence 5 a ±10 percent deviation in specific fuel consumption resulted in a -0. 4 to 0. 7 per-
cent change in the climb and acceleration performance of an F-111B airplane at maxi-
mum power.
A second assumption that must be made for equation (4) to be valid is that the pre-
dicted propulsion system characteristics available for the airplane are consistent within
themselves. It is also assumed that the relationship of the thrust and fuel flow is accu-
rately described and that the temperature corrections for these quantities are accurate.

If these assumptions are valid, the in-flight thrust can be calculated with equation (4)
by measuring the fuel flow and making use of the predicted propulsion system charac-
teristics of the airplane as follows:
F=(W./W_ |F (6)
t f f Dx
The drag can then be determined from equation (3). With this technique the thrust and
drag of the airplane can be determined for each test point for use in the performance
model.
Rather than calculate the thrust and drag for each test point, it was easier to use a
model which incorporated the predicted drag, thrust, and fuel flow and then to refine
these values by determining a set of coefficients, Kp and K^, so that the performance
of the model matched the test-day performance of the airplane. This was done by first
computing the coefficient Kp as defined by equation (6) as follows:
K = W /W = F/F (7)
F
*
f
t
f
*P *
t nPt
t
The coefficient K was then determined (for test conditions) from the following version
D
of equation (3):
\V~
(KFFp - KDD ^
t P + 8
, W) < >
" (dt
model x airplane
where
KD = Dt/D (9)
p
Values of Kp and KQ were determined in this manner for each point in a test trajec-
tory, and since values of predicted thrust and drag were available in the model, the
true thrust and drag of the airplane were readily calculated.
The data analysis procedures used in this investigation are discussed in detail in
the appendix.
VALIDATION OF THE PERFORMANCE MODELING TECHNIQUE
The performance modeling technique was validated on the basis of the following
criterion: That having determined a set of coefficients (Kp and KQ) from a series of
level accelerations performed at different altitudes, weights, and temperatures over the
flight envelope of an airplane, it should be possible to calculate the performance of the
airplane for any arbitrary flight trajectory encompassing climbs, dives, and accelera-
tions as long as the maneuvering load factor increments are low (±0. 2g). For the

validation, the modeling technique was applied to level acceleration flight-test data
obtained on an instrumented F-104G prototype airplane (fig. 2) and reported in refer-
ence 6.
The F-104G is a fixed-wing, fixed-inlet-geometry airplane powered by a J79-GE-11A,
high-pressure-ratio, afterburning turbojet engine. The airplane is 16.7 meters
(54. 8 feet) in length and 4. 1 meters (13. 5 feet) in height, with a wingspan of 6.7 meters
(21. 9 feet) and a sea-level ratio of maximum power thrust to weight of 0. 78. The test
instrumentation, the airplane, and the engine are described in detail in references 6,
7, and 8, respectively.
Model Coefficients Computed From Level Acceleration Maneuvers
The model coefficients K and K were determined from the level acceleration
F D
flight-test data using a computer program. (See appendix.) The coefficients computed
for two level acceleration maneuvers at an altitude of 9144 meters (30,000 feet) are
presented in figure 3 together with curves faired through each set of coefficients. The
analysis procedure was then repeated for level accelerations made at 3048 meters
(10,000 feet), 6096 meters (20,000 feet), 9144 meters (30,000 feet), 12,192 meters
(40,000 feet), and 15,240 meters (50,000 feet) to define the model coefficients for each
of these test altitudes. The fairings of the coefficients K-p and Kp obtained from
this analysis are presented in figures 4 and 5, respectively.
A complete performance model of the F-104G test airplane was then obtained by
combining the set of model coefficients presented in figures 4 and 5 with the predicted
aerodynamic and propulsion system characteristics of the airplane (tables 1 to 4, adapted
from refs. 7 and 8) in a digital trajectory analysis computer program. To validate the
coefficients, the trajectory program, which constitutes the performance model of the
test airplane, was used to compute the model test-day performance for each of the level
accelerations, with the test-day Mach number-altitude profile and the test-day tempera-
tures at altitude used as inputs to the program. Computed and measured test-day per-
formance of the airplane for the level accelerations made at 9144 meters (30, 000 feet)
is compared in figures 6(a) and 6(b). As shown, an excellent match was obtained, thus
validating the coefficients for this altitude. The coefficients for the other altitudes were
validated in the same manner. The performance model for the test airplane was
obtained from approximately 31 minutes of flight-test data.
The computer model could also have been obtained by adjusting the predicted drag
polars and the thrust and fuel flow curves in proportion to the model coefficients K-p
and KQ and then entering these new curves into the program. Although this approach
was notjised because of the time required to adjust and reprogram the curves each time
a coefficient was changed, typical adjusted and predicted drag polars for Mach numbers
of 0. 90 and 1. 60 are presented in figures 7(a) and 7(b).
Validation of the Model Using Arbitrary Profiles
To evaluate the validity of the performance model as a whole, model and measured
performance for other, arbitrarily chosen flight profiles were compared. The

performance of the test airplane was measured along three different flight profiles
flown from a Mach number of approximately 0. 90 at an altitude of 3048 meters
(10, 000 feet) to a Mach number of 2. 0 at an altitude of 12,192 meters (40, 000 feet).
The criterion established to validate the model was that the model and the measured
performance of the airplane agree within 5 percent.
The measured performance of the airplane and the computed performance of the
model are compared in figures 8(a) to 8(c). The width of the ±5 percent band about
the flight data curve indicates the region within which the model data should fall for a
satisfactory match. As shown in figure 8(a), a good match of the model and measured
performance was obtained for the first flight profile. But for the other two flight pro-
files (figs. 8(b) and 8(c)), the computed performance does not agree with the measured
performance of the airplane within the established 5 percent limit. Approximately 50
percent to 60 percent of the climb in flights B and C was at Mach numbers of 0. 95 to
1. 0, whereas only 5 percent of the climb in flight A was at these Mach numbers. Thus
inaccuracies in the predicted airplane aerodynamics and in the flight-test data in this
transonic region, coupled with the length of time spent at these Mach numbers, could
'iave been responsible for the errors encountered at the higher Mach numbers. Conse-
quently, the measured performance of the airplane and the computed performance of
:he model were compared for the supersonic portions of the flight profiles presented in
'igures 8(b) and 8(c). The comparisons (figs. 9(a) and 9(b)) show good agreement of the
>erformance data, which verifies the basic assumptions and points out that improved
>redictions of aerodynamic data, flight-test measurements, and test techniques are
leeded if the model coefficients in the transonic Mach number region are to be defined
nore accurately. Still, the validity of the modeling technique has been demonstrated,
md the time and effort required to produce this model has been substantially reduced.
Sensitivity of the Coefficients
From the preceding section and equations (6) and (9) it may be inferred that if the
model performance exactly matches the measured performance of the test airplane,
the in-flight thrust, fuel flow, and drag of the test airplane are defined accurately.
Therefore, errors in the values of in-flight thrust, fuel flow, and drag are due to the
errors in the final set of coefficients. The errors in the coefficients result from
instrumentation, measurement, and data analysis errors in the values of fuel flow,
altitude, velocity, rate of change of specific energy, and normal load factor. The
sensitivity of the model coefficients to variations in these parameters was determined
by increasing each parameter individually by 1 percent and determining the resulting
percentage of change in the coefficients. The results of the error determination are
presented in figure 10. As shown in figure 10(a), the coefficient KQ is sensitive to
errors in fuel flow, normal load factor, and rate of change of specific energy, es-
pecially at Mach numbers less than 1. 0. For example, a 1 percent error in fael flow
at Mach 0.75 results in a 4. 5 percent change in the value of K . The results are sen-
D
sitive to altitude at subsonic and supersonic speeds.
Because of the order in which the parameters were used in the modeling analysis,
fuel flow was the only parameter which influenced the value of the model coefficient K-p.
The variation in K caused by a 1 percent increase in the fuel flow (fig. 10(b)) shows
F

that it is sensitive to error in this parameter. Thus the quality of the model coeffi-
cients depends on the accuracy with which the flight-test fuel flow, normal load factor,
and altitude can be measured and on the accuracy with which the rate of change of
specific energy can be calculated. \
Extension of Modeling Technique
The results of the validation show that a realistic performance model of an airplane
can be defined with the modeling technique used in this study and that the assumptions
made in the development of the technique were valid. However, to develop a complete
performance model of an airplane, the modeling techniques must be extended to cover
both partial power and maneuvering flight conditions. Also, the technique was demon-
strated only with a fixed-wing, fixed-inlet-geometry airplane. For a complete evalua-
tion it should be extended to airplanes with variable wing sweep, variable inlet geome-
try, or both. Application of the modeling technique to any. airplane is dependent on
the ability to account for variations in the aerodynamic and propulsion system param-
eters resulting from variations in test-day temperatures and aircraft weight.
CONCLUDING REMARKS
A technique for defining an airplane performance model in terms of thrust and drag
from flight-test data and predicted aerodynamics and propulsion system characteristics
of the airplane was developed. With the modeling technique, a nominal Ig performance
model was defined for the entire flight envelope of an F-104G airplane from approxi-
mately 31 minutes of flight-test data. Use of the technique could substantially reduce
the time required for performance flight testing and produce a clear definition of the
thrust and drag of an aircraft.
The study showed the sensitivity of the model coefficients to errors in measured
and calculated flight-test parameters. The model coefficient for drag was sensitive to
errors in fuel flow, normal load factor, altitude, and rate of change of specific energy,
and the model coefficient for thrust was sensitive to errors in fuel flow. The accuracy
of the performance model defined was therefore dependent on the accuracy with which
these flight-test parameters were measured and calculated.
The performance modeling technique was evaluated with flight-test data from the
F-104G airplane. The model performance matched the flight-test performance within
5 percent except where large portions of a trajectory were flown at transonic Mach
numbers. This lack of agreement pointed out the need for improved flight-test
measurements, test techniques, and predicted aerodynamic data if the model coeffi-
cients in the transonic Mach number region are to be defined more accurately.
The modeling technique was demonstrated only with a fixed-wing, fixed-inlet-
geometry airplane. It should be extended to airplanes with variable wing sweep,
variable inlet geometry, or both, for complete evaluation. Also, to develop a com-
plete performance model of an airplane, the modeling technique must be extended to
cover partial power and maneuvering flight conditions.
Flight Research Center,
National Aeronautics and Space Administration,
Edwards, Calif., June 28,1972.

APPENDIX
PERFORMANCE MODELING DATA ANALYSIS PROCEDURES
The performance modeling techniques and data analysis procedures used to define
a performance model for an F-104G airplane from level acceleration flight-test data
are outlined in the following discussion.
The model coefficients Kp and K were computed from flight-test data, pre-
D
dicted aerodynamic and propulsion system characteristics given in references 7 and 8,
and equations (Al to A12). The flight-test parameters used to compute the coefficients •
were test-day true velocity, V, pressure altitude, h, Mach-number, M, angle of
t t t
attack, a, total fuel flow, Wf , normal load factor, N, and ambient temperature at
altitude, T .
a
I
The instantaneous specific energy (or total energy per pound) of the airplane was
computed for each data point as follows:
V2
he = h+lt_ (Al)
t t
2g
The rate of change of the specific energy was then computed by determining the slope at
each test point of a smooth curve fitted to a time history of he^.
The engine and afterburner fuel-used values for the test airplane were computed
for each data point and summed to obtain the instantaneous total fuel used, FU, for the
airplane. Instantaneous airplane weight was determined by subtracting the total fuel
used at each data point from the airplane weight at engine start. The flight-test fuel
flow was then obtained by determining the slope at each data point of a curve fitted to a
time history of the total fuel used for each level acceleration with the following equation:
t
The predicted standard-day values of thrust and fuel flow for the test airplane were
obtained from curves given in reference 7 for a maximum afterburner power setting by
using the expressions ;
F = f(M,h) (A3)
p t
W =f(M, hJ (A4)
f
P
To compute the predicted test-day values of thrust and fuel flow, the changes in thrust,

AF,  and fuel flow,  AW^,  resulting from nonstandard day temperatures were computed.
|     |     |     | AF/6 | /6  |     |
| --- | --- | --- | ---- | --- | --- |
  AWf
Values of  AF  and  AW  were obtained from plots of  -=;  =-  and  -=  =-  versus
| 1  f |     |     | Ts~Tt  | Ts~Tt |     |
| ---- | --- | --- | ------ | ----- | --- |
test-day total temperature, respectively.  The data for these plots were obtained from
reference 8.  The test-day total temperature at altitude was determined from the Mach
number and ambient temperature, and the change in thrust and fuel flow was computed
as follows:
AF
| AF = -—s_  |        | (T. - T)  | 6.   |     | (A5) |
| ---------- | ------ | --------- | ---- | --- | ---- |
|            | Ts~Tt  | s         | r  t |     |      |
W
AW
f
(A6)
The model coefficient  K   was calculated for each data point with the expression
F
W*
(A7)
|     |     | /W  + AW \ |     |     |     |
| --- | --- | ---------- | --- | --- | --- |
|     |     | f          | f   |     |     |
The flight -test thrust of the airplane was then computed by using the expression
|     | F  = (F | +AF)K |     |     | (AS) |
| --- | ------- | ----- | --- | --- | ---- |
|     | t       | p     | F   |     |      |
The total flight -test drag of the airplane was computed as  follows:
To compute the model coefficient  K^,  the predicted flight -test drag of the airplane
was calculated.  The predicted drag coefficient was then obtained from the aerodynamic
data presented in reference 1 by using the equation
|     | C   | = f/C  , M\  |     |     | (A10) |
| --- | --- | ------------ | --- | --- | ----- |
|     | D   | L            |     |     |       |
|     | p   | V  t         | /   |     |       |
where
CL~ q{
t
The predicted drag of the test airplane for each data point was computed as follows:
|     | D   |  = C qS  |     |     | (All) |
| --- | --- | -------- | --- | --- | ----- |
|     | p   | Dp       |     |     |       |
10

The model coefficient K was computed for each data point using the results of
D
equations (A9) and (All) and the expression
KD = Dt/Dp
The values of the model coefficients K/p and KQ were plotted against Mach num
ber for each altitude at which a level acceleration maneuver was performed. Then a
curve was faired through each set of coefficients. These fairings were combined with
the predicted aerodynamic and propulsion system characteristics of the airplane in a
two-dimensional trajectory analysis program to define the performance model of the
test airplane.
11

REFERENCES
1. Mechtly, E. A.: The International System of Units - Physical Constants and Con-
version Factors. NASA SP-7012, 1969.
2. Herrington, Russel M.; Shoemacher, Paul E.; Bartlett, Eugene P.; and Dunlap,
Everett W.: Flight Test Engineering Handbook. Tech. Rep. No. 6273, Air Force
Flight Test Center, May 1951 (rev. Jan. 1966).
3. Godwin, O. D.; Frazier, F. D.; and Durnin, R. E.: Performance Flight Test
Techniques. FTC-TIH 64-2006, USAF Aerospace Research Pilot School, Edwards
Air Force Base, Calif. [1964].
4. Hendrix, George D.; Godwin, Orgle D.; Frazier, Frank D.; and Durnin, Rodney E. :
Performance Flight Testing Theory. FTC-TIH 64-2005, USAF Aerospace
Research Pilot School, Edwards Air Force Base, Calif. [1964].
5. Irons, Robert P. , Jr.; Lindquist, O. H.; Schultz, R. L.; et al.: Integrated Engine
Instrumentation System Study - Energy Management Subsystem Investigation.
Volume 1: Basic Document. Rept. No. 12591-FR1 vol. 1, Honeywell, Inc.,
Apr. 1970. (Available from DDC as AD 872130.)
6. Marshall, Robert T.: Flight-Determined Acceleration and Climb Performance of
an F-104G Airplane for Use in an Optimum-Flight-Path Computer Program.
NASA TN D-6398, 1971.
7. Avant, N. J.: Performance Characteristics - Appendix A. Rep. No. 16097 App. A,
Lockheed Aircraft Corp., July 16, 1962.
8. Michaels, J. M.; Wesling, G. C.; Housley, F. R.; and Henderson, R. L.:
J79-GE-7, J79-GE-11, J79-GE-11A Turbojet Engine. R60FPD451. Flight Pro-
pulsion Div., General Electric, Sept. 1960.
12

TABLE 1
VALUES OF LIFT COEFFICIENT FOR THE F-104G AIRPLANE AT SPECIFIC ANGLES
OF ATTACK AND MACH NUMBERS
|     |     |     |     |     | C   for an M of - |     |     |     |     |
| --- | --- | --- | --- | --- | ----------------- | --- | --- | --- | --- |
TL
a,
| deg | 0.4 | 0.6 | 0.8 | 0.9 | 1.0 | 1.2 | 1.4 | 1.6 1.8 | 2.0 |
| --- | --- | --- | --- | --- | --- | --- | --- | ------- | --- |
0 0.010 0.010 0.010 0.010 -0.010 -0.020 0.040 0.032 0.020 0.010
| 2   | .100 | .100 | .118 | .145 | .140 | .125 | .155 | .132 .110 | .090 |
| --- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | --------- | ---- |
| 4   | .210 | .215 | .270 | .300 | .300 | .255 | .275 | .235 .200 | .175 |
| 6   | .318 | .330 | .415 | .465 | .450 | .380 | .390 | .340 .290 | .252 |
| 8   | .430 | .445 | .535 | .610 | .600 | .515 | .500 | .440 .380 | .330 |
| 10  | .540 | .555 | .630 | .720 | .740 | .650 | .618 | .540 .470 | .409 |
| 12  | .655 | .659 | .710 | .800 | .868 | .765 | .720 | .639 .559 | .480 |
| 14  | .743 | .748 | .775 |      | .980 | .870 | .820 | .730 .642 | .560 |
.870 TABLE 2
VALUES OF DRAG COEFFICIENT FOR THE F-104G AIRPLANE AT SPECIFIC MACH
NUMBERS AND LIFT COEFFICIENTS
|     |     |      |      |      | C_  for a  | C   of - |      |           |      |
| --- | --- | ---- | ---- | ---- | ---------- | -------- | ---- | --------- | ---- |
|     |     |      |      |      | D          | LTJ      |      |           |      |
| M   | 0   | 0.10 | 0.15 | 0.20 | 0.25       | 0.30     | 0.35 | 0.40 0.45 | 0.50 |
0 0.0160 0.0175 0.0195 0. 0222 0. 0258 0.0308 0.0378 0.0462 0.0562 0.0673
.0378 .0462 .0673
.800 .0160 .0175 .0195 .0222 .0258 .0308 .0562
.850 .0163 .0180 .0197 .0220 .0260 .0315 .0387 .0475 .0575 .0683
.880 .0170 .0184 .0200 .0228 .0269 .0329 .0402 .0491 .0591 .0700
.900 .0170 .0185 .0203 .0233 .0278 .0335 .0408 .0495 .0600 .0718
.925 .0190 .0200 .0219 .0250 .0295 .0357 .0431 .0521 .0632 .0755
.950 .0230 .0240 .0268 .0305 .0355 .0417 .0488 .0578 .0685 .0802
.975 .0310 .0338 .0357 .0383 .0428 .0488 .0562 .0652 .0752 .0880
1.000 .0380 .0401 .0420 .0455 .0509 .0575 .0650 .0738 .0852 .0983
1.050 .0470 .0485 .0512 .0555 .0606 .0670 .0763 .0870 .0990 .1118
1.100 .0500 .0520 .0550 .0595 .0653 .0740 .0820 .0913 .1040 .1175
1.150 .0500 .0522 .0555 .0599 .0661 .0739 .0830 .0940 .1059 .1210
1.200 .0490 .0519 .0553 .0602 .0669 .0750 .0850 .0959 .1088 .1235
1.400 .0468 .0495 .0535 .0589 .0663 .0758 .0870 .1000 .1145 .1305
1.600 .0440 .0470 .0515 .0579 .0663 .0770 .0895 .1038 .1193 .1360
1.800 .0430 .0472 .0523 .0591 .0685 .0798 .0930 .1085 .1250 .1435
.0960 .1315 .1515
| 2.000 | .0422 | .0463 | .0519 | .0590 | .0689 | .0815 |     | .1130 |     |
| ----- | ----- | ----- | ----- | ----- | ----- | ----- | --- | ----- | --- |
13

TABLE 3
VALUES OF NET THRUST FOR THE F-104G AIRPLANE AT SPECIFIC
ALTITUDES AND MACH NUMBERS
|     |     |     |     |     | F,  in N (Ib), for an  | M   | of- |     |     |     |
| --- | --- | --- | --- | --- | ---------------------- | --- | --- | --- | --- | --- |
h,
| w (ft) | 0   | 0.4 | 0.6 | 0.8 | 1.0 | 1.2 | 1.4 | 1.6 | 1.8 | 2.0 |
| ------ | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
0 49,820 60,673 66,945 74,596 84,961 95,859 106,534 117,210 127,886 138,561
(0) (11,200) (13,640) (15,050) (16,770) (19,100) (21,550) (23,950) (26,350) (28,750) (31,150)
3,048 34,251 44,704 51,154 58,716 67,168 76,509 89,409 102,309 115,653 128, 998
(10,000) (7,700) (10,050) (11,500) (13,200) (15,100) (17,200) (20,100) (23,000) (26,000) (29, 000)
6,096 20,684 30,559 36, 920 43,948 51,822 60, 940 71,972 81,180 89,409 97,860
(20,000) (4,650) (6,870) (8,300) (9,880) (11,650) (13,700) (16,180) (18,250) (20, 100) (22, 000)
9,144 15,124 23,042 26,912 31,137 37,810 45,372 54,224 62,186 70,415 75,842
(30,000) (3,400) (5,180) (6,050) (7,000) (8,500) (10,200) (12,190) (13,980) (15,830) (17,050)
12,192 13,478 16,903 18,593 20,462 23,575 28, 246 34,918 41,947 48,218 54,401
(40,000) (3, 030) (3,800) (4, 180) (4,600) (5,300) (6,350) (7,850) (9,430) (10,840) (12,230)
15,240 7,562 10,008 11,209 12,544 14,457 17,215 21,440 26,111 29, 936 33,273
(2,520)
(50,000) (1,700) (2, 250) (2, 820 (3,250) (3,870) (4,820) (5,870) (6,730) (7,480)
18,288 1,779 4,671 6,183 7,562 9,030 10,809 13,300 16,014 18,682 20,551  '
(1,390)
(60,000) (400) (1,050) (1,700) (2, 030) (2,430) (2, 990) (3,600) (4,200) (4,620)
TABLE 4
VALUES OF FUEL FLOW RATE FOR THE F-104G AIRPLANE AT SPECIFIC
ALTITUDES AND MACH NUMBERS
|     |     |     |     | Fuel flow rate, in kg/sec (Ib/sec), for an  |     |     | M   | of- |     |     |
| --- | --- | --- | --- | ------------------------------------------- | --- | --- | --- | --- | --- | --- |
h,
| m  (ft) | 0    | 0.4  | 0.6  | 0.8  | 1.0  | 1.2  | 1.4  | 1.6  | 1.8  | 2.0   |
| ------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ----- |
|         | 3.23 | 3.97 | 4.42 | 5.01 | 5.86 | 6.83 | 7.80 | 8.77 | 9.74 | 10.71 |
0
(0) (7.13) (8.75) (9.75) (11.05) (12.91) (15.05) (17.19) (19.33) (21.47) (23.61)
| 3,048 | 2.23 | 2.89 | 3.27 | 3.74 | 4.36 | 5.14 | 5.92 | 6.80 | 7.68 | 8.56 |
| ----- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
(10,000) (4.91) (6.38) (7.22) (8. 25) (9.62) (11.33) (13.05) (15.00) (16.94) (18.88)
| 6,096 | 1.52 | 2.05 | 2.34 | 2.68 | 3.13 | 3.75 | 4.47 | 5.30 | 6.01 | 6.71 |
| ----- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
(20,000) (3.36) (4.52) (5.16) (5.91) (6.91) (8.27) (9.86) (11.69) (13.25) (14.80)
| 9,144 | 1.01 | 1.43 | 1.65 | 1.89 | 2.21 | 2.63 | 3.15 | 3.73 | 4.30 | 4.79 |
| ----- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
(30,000) (2.22) (3.16) (3.63) (4.16) (4.88) (5.80) (6.94) (8.22) (9.47) (10.55)
| 12,192 | .50 | .91 | 1.11 | 1.32 | 1.55 | 1.81 | 2.15 | 2.55 | 2.93 | 3.20 |
| ------ | --- | --- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
(40, 000) (1.11) (2. 00) (2.44) (2.91) (3.41) (4. 00) (4.75) (5.63) (6.47) (7.05)
| 15,240 | .34 | .63 | .77 | .91 | 1.06 | 1.22 | 1.43 | 1.67 | 1.90 | 2.05 |
| ------ | --- | --- | --- | --- | ---- | ---- | ---- | ---- | ---- | ---- |
(50, 000) (.75) (1.38) (1.69) (2.00) (2.33) (2.69) (3.16) -<3.69) (4.19) (4.52)
| 18,288 | .04 | .30 | .43 | .55 | .68 | .80 | .94 | 1.08 | 1.22 | 1.31 |
| ------ | --- | --- | --- | --- | --- | --- | --- | ---- | ---- | ---- |
(60,000) (.08) (.66) (.94) (1.22) (1.50) (1.77) (2.08) (2.38) (2.69) (2.88)
14

I
G,
O 090 O —i
S
oo I
•rH
X
c
O rt
s
•a
o
t>
ro
CD
a
CT> O>
iZ <
c
o • o
s
3
M
€
O
o
o
•rH
<+H
•rH
00 0«D O
CO
TJ
a
o
s
3
CO
c«
<U
S
_o
I
Q-
o •
rH
CO
S,
15

o
2
16

w
*H
-S
o Va
CVJ
00 •8
^H CSJ
ci
o
-Ift
0)
r—I
O
u
rt
i—i
0>
5
0I)
a
s
I
'i
a
2
OO
a «i
o a
U FH
W rt
£S
"S h
i—i ^
(D tj
cvj o oo •Q O
O <M
17

h, m (ft)
15,240(50,000)
1.0
K .8
r
.6 12,192(40,000)
1.0
.8 .6
9,144(30,000)
1.0
.8 .6
6096(20,000)
1.0
-8
.6 1.2 1 —
i n 3048(10.000)
1. U
/^ ^
.8 1 1 1 1
.6 .4 .6 .8 1.0 1.2 1.4 1.6 1.8 2.0
M
Figure 4. Computed values of model coefficient K-r, for thrust and fuel flow for the
flight envelope of an F-104G airplane.
18

h, m (ft)
1.0
15,240(50,000)
8
.6 1.2
1.0 12,192(40,000)
D -8
.6 .4
1.4
1.2
K
9144(30,000)
1.0
.8 1.2
6096(20,000)
1.0
K
.8 .6
1.6
1.4
1.2
3048(10,000)
D 1-0
.8 .6
.4 .4 .6 .8 1.0 1.2 1.4 1.6 1.8 2.0
M
Figure 5. Computed values of model coefficient K for drag for the flight envelope of
D
an F-104G airplane.
19

Flight data
o Model data
800
1500
1000
FU, kg 400
FU, Ib
500
0
300 i-
t. sec
9500
o—o- 30X103
h. m
h. ft
7500 25
.6 .8 1.0 1.2 I.- 1.6 1.8 2.0
M
(a) Maneuver 1. •
i
Figure 6. Comparison of flight-test data and model-derived data for a maximum power
level acceleration of an F-104G airplane.
20

Flight data
o Model data
800
1500
1000
FU, kg 400
FU, Ib
500
0
300 r-
200
t, sec
100
9500
o—o—o—o- -o—o—o—o 30xlOJ
h, m
h, ft
7500 25
.6 .8 1.0 1.2 1.4 1.6 1.8 2.0
M
(b) Maneuver 2.
Figure 6. Concluded.
21

.6 o Model data
Predicted
.4 .2
.02 .04 .06 .08 .10
Cn
(a) M =0.90.
.6 o Model data
— Predicted
.4 .2
0 .02 .04 .06 .08 .10 .12 .14
CD
(b) M = 1.60.
Figure 7. Comparison of adjusted model and predicted drag polars for an F-104G air-
plane in a clean configuration.
22

Flight data
o Model data
- ±5 percent band
1200
2500
2000
800
1500
FU, kg
FU. Ib
1000
400
500
0
300 i—
t, sec
h, m
.8 -1.0 1.2 1.4 1.6 1.8 2.0
(a) Flight A.
Figure 8. Comparison of flight-test data and model-derived data for maximum power
climb of an F-104G airplane.
23

— Flight data
o Model data
li': ±5 percent band
1200 r-
800 -
FU, kg FU. Ib
400 -
t. sec
h. m
2.0
(b) Flight B.
Figure 8. Continued.
24

Flight data
o Model data
; ±5 percent band
1200 j-
2500
2000
800 -
1500
FU, kg FU. Ib
'1000
400 -
500
0 0
300
200
t. sec
100
0
12 x 103 40X1Q3
36
10
32
•o—o—o—o-
28
24 h, ft
h. m
20
16
12
I 8
.8 1.0 1.2 1.4 1.6 1.8 2.0
M
(c) Flight C.
Figure 8. Concluded.
25

Flight data
Model data
± 5 percent band
1200
2500
2000
800
1500
FU, kg FU, Ib
1000
400
500
0
300 i-
200
t. sec
100
12 x 103 40x10^
36
10
32
28
24 h, ft
h, m
20
16
12
8
.8 1.0 1.2 1.4 1.6 1.8 2.0
M
(a) Flight B.
Figure 9. Comparison of flight-test data and model-derived data for the supersonic
portion of a flight of an F-104G airplane.
26

Flight data
o Model data
* ±5 percent band
s<f
1200
2500
2000
800
1500
FU, kg FU, Ib
1000
400
500
0
300 i—
200
t. sec
100
0
40X1Q3
12 x10J
36
.10 32
28
24 h, ft
h, m
20
16
12
8
.8 1.0 1.2 1.4 1.6 1.8 2.0
M
(b) Flight C.
Figure 9. Concluded.
27

KD(h).
percent
K (V), 2 r
D
percent I
0
K (W), 4
D f
percent 2
0
K (N), 0
D
percent _
2
K
Ddt
percent
.5 1.0 1.5 2.0
M
(a) K .
D
r
K (W),
F f
percent
.5 1.0 1.5 2.0
M
(b)K.
f
Figure 10. Percentage of change in model coefficients K and K resulting from
D F
a 1 percent increase in important parameters.
28 NASA-Langley, 1973 2 H~723

NATIONAL AERONAUTICS AND SPACE ADMINISTRATION
WASHINGTON. D.C. 2O546
POSTAGE AND FEES PAID
NATIONAL AERONAUTICS AND
|     | OFFICIAL BUSINESS |     |     |         |     |              |     |      | SPACE  | ADMINISTRATION |
| --- | ----------------- | --- | --- | ------- | --- | ------------ | --- | ---- | ------ | -------------- |
|     |                   |     |     | SPECIAL |     | FOURTH-CLASS |     | RATE |        | 451            |
PENALTY FOR PRIVATE USE S3OO
BOOK
If Undeliverable (Section 158
|       |     |             |                                                           |            |                              |                                           |            |                        | POSTMASTER :    | Postal Manual) Do Not Return |
| ----- | --- | ----------- | --------------------------------------------------------- | ---------- | ---------------------------- | ----------------------------------------- | ---------- | ---------------------- | --------------- | ---------------------------- |
|       |     |             | "The  aeronautical                                        |            | and space activities of the  |                                           |            | United States shall be |                 |                              |
|       |     |             | conducted so as to contribute                             |            |                              | . . . to the                              | expansion  |                        | of human knowl- |                              |
|       |     |             | edge of phenomena in the atmosphere and space. The        |            |                              |                                           |            |                        | Administration  |                              |
|       |     |             | shall provide for the widest                              |            |                              | practicable and appropriate dissemination |            |                        |                 |                              |
|       |     |             | of information concerning its activities and the results  |            |                              |                                           |            |                        | thereof."       |                              |
|       |     |             |                                                           | —NATIONAL  |                              | AERONAUTICS                               | AND SPACE  |                        | ACT OF 1958     |                              |
| NASA  |     | SCIENTIFIC  |                                                           |            | AND                          | TECHNICAL                                 |            |                        | PUBLICATIONS    |                              |
TECHNICAL  REPORTS:  Scientific and TECHNICAL  TRANSLATIONS:  Information
technical information considered important, published in a foreign language considered
complete, and a lasting contribution to existing to merit NASA distribution in English.
knowledge.
|     |            |     |                               |     |     |     | SPECIAL  | PUBLICATIONS:  |     | Information |
| --- | ---------- | --- | ----------------------------- | --- | --- | --- | -------- | -------------- | --- | ----------- |
|     | TECHNICAL  |     | NOTES: Information less broad |     |     |     |          |                |     |             |
derived from or of value to NASA activities.
in scope but nevertheless of importance as a
contribution  to existing knowledge. Publications include final reports of major
projects, monographs, data compilations,
|     | TECHNICAL  |     | MEMORANDUMS: |     |     |     |             |                          |     |     |
| --- | ---------- | --- | ------------ | --- | --- | --- | ----------- | ------------------------ | --- | --- |
|     |            |     |              |     |     |     | handbooks,  | sourcebooks, and special |     |     |
Information receiving limited distribution
bibliographies.
because of preliminary data, security classifica-
tion, or other reasons. Also includes conference
TECHNOLOGY UTILIZATION
proceedings with either limited or unlimited
|     |     |     |     |     |     |     | PUBLICATIONS:  |     | Information on  | technology |
| --- | --- | --- | --- | --- | --- | --- | -------------- | --- | --------------- | ---------- |
distribution.
|     |     |     |     |     |     |     | used by NASA  |     | that may be of particular |     |
| --- | --- | --- | --- | --- | --- | --- | ------------- | --- | ------------------------- | --- |
CONTRACTOR REPORTS: Scientific and interest in commercial and other non-aerospace
technical information generated under a NASA
applications. Publications include Tech Briefs,
contract or grant and considered  an important Technology Utilization Reports and
|     | contribution to existing knowledge. |     |     |     |     |     | Technology  | Surveys. |     |     |
| --- | ----------------------------------- | --- | --- | --- | --- | --- | ----------- | -------- | --- | --- |
Details  on the availability of  these publications  may be obtained  from:
|           |     |     | SCIENTIFIC AND  |     |              | TECHNICAL INFORMATION  |            |     | OFFICE         |     |
| --------- | --- | --- | --------------- | --- | ------------ | ---------------------- | ---------- | --- | -------------- | --- |
| NATIONAL  |     |     | AERONAUTICS     |     |              | AND                    | SPACE      |     | ADMINISTRATION |     |
|           |     |     |                 |     | Washington,  |                        | D.C. 20546 |     |                |     |