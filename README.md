# awesome-progressbar-widget

An awesome widget (3.4 only). Based on blingbling widgets. Horribly unoptimised, has bugs.

It was created because blingbling widgets use cairo font rendering which looks horrible and 
lacks some characters rendering boxes instead. This widget uses pango for text, which saves us
from boxes and can render virtually everything. It also looks prettier.


Features:
* Fixed-size progressbar with visual track progress and track name
* On-click notification with track, artist name, cover etc.

![progressbar](https://github.com/unknown321/awesome-progressbar-widget/raw/master/progressbar.png)

![notification](https://github.com/unknown321/awesome-progressbar-widget/raw/master/notification.png)


Requires oocairo and lgi because awesome 3.4 sucks.
