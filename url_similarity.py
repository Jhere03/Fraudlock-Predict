from flask import Flask, request, jsonify
import socket
from urllib.parse import urlparse
import difflib
import argparse
import os


app = Flask(__name__)

# Lista de dominios conocidos de compras
KNOWN_DOMAINS = [
"amazon.com",
"ebay.com",
"walmart.com",
"target.com",
"bestbuy.com",
"newegg.com",
"etsy.com",
"homedepot.com",
"lowes.com",
"macys.com",
"nordstrom.com",
"zappos.com",
"aliexpress.com",
"rakuten.com",
"shopify.com",
"wayfair.com",
"etsy.com",
"asos.com",
"boohoo.com",
"farfetch.com",
"myntra.com",
"flipkart.com",
"snapdeal.com",
"jd.com",
"dhgate.com",
"lazada.com",
"zalando.com",
"carrefour.com",
"tesco.com",
"marksandspencer.com",
"sainsburys.co.uk",
"argos.co.uk",
"aldi.co.uk",
"lidl.com",
"mercadolibre.com",
"olx.com",
"tokopedia.com",
"bukalapak.com",
"jd.id",
"ruten.com.tw",
"yesstyle.com",
"kabum.com.br",
"shein.com",
"uniqlo.com",
"harrods.com",
"selvagedenim.com",
"mrporter.com",
"nike.com",
"adidas.com",
"puma.com",
"lululemon.com",
"decathlon.com",
"rei.com",
"patagonia.com",
"levis.com",
"gap.com",
"oldnavy.com",
"hm.com",
"forever21.com",
"urbanoutfitters.com",
"abercrombie.com",
"hollisterco.com",
"anthropologie.com",
"modcloth.com",
"bodenusa.com",
"talbots.com",
"carters.com",
"childrensplace.com",
"gymboree.com",
"jcrew.com",
"brooksbrothers.com",
"landsend.com",
"columbia.com",
"northface.com",
"patagonia.com",
"marmot.com",
"arcadebelts.com",
"vans.com",
"converse.com",
"toms.com",
"katespade.com",
"michaelkors.com",
"coach.com",
"fergusonshowrooms.com",
"kohler.com",
"build.com",
"wayfair.com",
"overstock.com",
"westelm.com",
"ikea.com",
"crateandbarrel.com",
"potterybarn.com",
"cb2.com",
"williams-sonoma.com",
"surlatable.com",
"bedbathandbeyond.com",
"cookstore.com",
"chewy.com",
"petsmart.com",
"petco.com",
"bhphotovideo.com",
"sweetwater.com",
"guitarcenter.com",
"adorama.com",
"musiciansfriend.com",
"gap.com",
"express.com",
"americaneagle.com",
"ae.com",
"universalstore.com",
"cottonon.com",
"pacsun.com",
"hottopic.com",
"zulily.com",
"boscovs.com",
"landsend.com",
"qvc.com",
"urbanoutfitters.com",
"freepeople.com",
"fossil.com",
"perfumania.com",
"bluefly.com",
"ashford.com",
"revolve.com",
"saksfifthavenue.com",
"bloomingdales.com",
"barneys.com",
"net-a-porter.com",
"matchesfashion.com",
"ssense.com",
"endclothing.com",
"tedbaker.com",
"allsaints.com",
"superdry.com",
"levi.com",
"fila.com",
"timberland.com",
"clarksusa.com",
"ugg.com",
"drmartens.com",
"reebok.com",
"birkenstock.com",
"toryburch.com",
"jimmychoo.com",
"stuartweitzman.com",
"swarovski.com",
"pandora.net",
"kay.com",
"jamesallen.com",
"brilliantearth.com",
"warbyparker.com",
"ray-ban.com",
"oakley.com",
"suncloudoptics.com",
"smithoptics.com",
"lenscrafters.com",
"zennioptical.com",
"glassesusa.com",
"contactsdirect.com",
"1800contacts.com",
"carmax.com",
"cars.com",
"truecar.com",
"cargurus.com",
"edmunds.com",
"autotrader.com",
"autozone.com",
"rockauto.com",
"napaonline.com",
"oreillyauto.com",
"pepboys.com",
"advanceautoparts.com",
"partsgeek.com",
"tirerack.com",
"discounttire.com",
"bicyclesonline.com.au",
"chainreactioncycles.com",
"evanscycles.com",
"biketiresdirect.com",
"cannondale.com",
"specialized.com",
"trekbikes.com",
"giant-bicycles.com",
"madison.co.uk",
"probikekit.com",
"wiggle.com",
"chainreactioncycles.com",
"rei.com",
"cabelas.com",
"basspro.com",
"dickssportinggoods.com",
"academy.com",
"sportsmansguide.com",
"golfgalaxy.com",
"tennisexpress.com",
"midwayusa.com",
"basspro.com",
"overtons.com",
"kayak.com",
"expedia.com",
"made.com",
"allmodern.com",
"mayfair.com",
"brooklinen.com",
"parachutehome.com",
"bollbranch.com",
"luxdeco.com",
"article.com",
"onekingslane.com",
"cb2.com",
"roomandboard.com",
"birchlane.com",
"westwingnow.de",
"grandinroad.com",
"overland.com",
"horchow.com",
"jossandmain.com",
"ballarddesigns.com",
"perigold.com",
"westelm.co.uk",
"thewhitecompany.com",
"serenaandlily.com",
"lovesac.com",
"modsy.com",
"roomstogo.com",
"lampsplus.com",
"homedecorators.com",
"arhaus.com",
"crateandbarrel.ca",
"hayneedle.com",
"designwithinreach.com",
"2modern.com",
"grainger.com",
"nfm.com",
"scandinavianhouse.com",
"restorationhardware.com",
"stylight.com",
"frontgate.com",
"improvements.com",
"builddirect.com",
"greentoe.com",
"castlery.com",
"urbanladder.com",
"pepperfry.com",
"royaloakindia.com",
"ifurn.com.au",
"templeandwebster.com.au",
"trendshome.com",
"zansaar.com",
"featherandblack.com",
"finnishdesignshop.com",
"vivaterra.com",
"hay.dk",
"fritz-hansen.com",
"gubi.dk",
"hugohome.com",
"thegioididong.com",
"viettelstore.vn",
"sendo.vn",
"bachhoaxanh.com",
"lazada.vn",
"tiki.vn",
"vinabook.com",
"thegioigiay.com",
"zigzagshop.vn",
"govilniya.com",
"foody.vn",
"now.vn",
"shoppy.vn",
"adayroi.com",
"dienmayxanh.com",
"elcorteingles.es",
"fnac.com",
"darty.com",
"bol.com",
"coolblue.nl",
"cdiscount.com",
"conforama.fr",
"castorama.fr",
"bricodepot.fr",
"fnac.pt",
"worten.pt",
"pcdiga.com",
"meo.pt",
"pik.ba",
"limundograd.com",
"anibis.ch",
"galaxus.ch",
"digitec.ch",
"microspot.ch",
"toppreise.ch",
"amazon.fr",
"amazon.de",
"amazon.es",
"amazon.it",
"amazon.co.uk",
"otto.de",
"ebay.de",
"zalando.de",
"mediamarkt.de",
"saturn.de",
"cdiscount.fr",
"pixmania.fr",
"boulanger.com",
"rueducommerce.fr",
"bhv.fr",
"eprice.it",
"monclick.it",
"yeppon.it",
"misterbuy.it",
"trony.it",
"mediaworld.it",
"redcoon.it",
"gamestop.it",
"ikea.it",
"zalando.it",
"subito.it",
"venditoreaffidabile.it",
"wish.com",
"gearbest.com",
"banggood.com",
"dx.com",
"tomtop.com",
"geekbuying.com",
"lightinthebox.com",
"miniinthebox.com",
"dhgate.com",
"cafago.com",
"joybuy.com",
"alibaba.com",
"made-in-china.com",
"toysrus.com",
"hamleys.com",
"buildabear.com",
"lego.com",
"hotwheels.com",
"playmobil.us",
"mattel.com",
"hasbro.com",
"disneystore.com",
"nintendo.com",
"sony.com",
"microsoftstore.com",
"apple.com",
"hp.com",
"dell.com",
"lenovo.com",
"asus.com",
"acer.com",
"toshiba.com",
"panasonic.com",
"samsung.com",
"lg.com",
"sony.com",
"philips.com",
"sharp.com",
"bose.com",
"sennheiser.com",
"jbl.com",
"beatsbydre.com",
"logitech.com",
"razer.com",
"steelseries.com",
"hyperxgaming.com",
"corsair.com",
"nzxt.com",
"coolermaster.com",
"thermaltake.com",
"evga.com",
"msi.com",
"gigabyte.com",
"asrock.com",
"intel.com",
"amd.com",
"nvidia.com",
"microcenter.com",
"neweggbusiness.com",
"bhphotovideo.com",
"abt.com",
"crutchfield.com",
"adorama.com",
"focuscamera.com",
"slickwraps.com",
"dbrand.com",
"zagg.com",
"otterbox.com",
"mophie.com",
"spigen.com",
"belkin.com",
"anchorfree.com",
"expressvpn.com",
"nordvpn.com",
"cyberghostvpn.com",
"purevpn.com",
"hidemyass.com",
"privateinternetaccess.com",
"tunnelbear.com",
"ivacy.com",
"surfshark.com",
"nike.co.uk",
"adidas.co.uk",
"cultbeauty.co.uk",
"beautybay.com",
"lookfantastic.com",
"feelunique.com",
"superdrug.com",
"boots.com",
"escentual.com",
"spacenk.com",
"asos.com",
"selfridges.com",
"harveynichols.com",
"houseoffraser.co.uk",
"johnlewis.com",
"marksandspencer.com",
"debenhams.com",
"next.co.uk",
"clarks.co.uk",
"schuh.co.uk",
"office.co.uk",
"very.co.uk",
"littlewoods.com",
"currys.co.uk",
"argos.co.uk",
"maplin.co.uk",
"richersounds.com",
"pcworld.co.uk",
"scan.co.uk",
"overclockers.co.uk",
"shop.bt.com",
"ebuyer.com",
"dabs.com",
"box.co.uk",
"jessops.com",
"wexphotovideo.com",
"lcegroup.co.uk",
"calumetphoto.co.uk",
"jigsaw-online.com",
"fatface.com",
"whistles.com",
"karenmillen.com",
"phase-eight.com",
"hobbs.com",
"jaeger.co.uk",
"coast-stores.com",
"reiss.com",
"frenchconnection.com",
"oasis-stores.com",
"warehouse.co.uk",
"topshop.com",
"missselfridge.com",
"newlook.com",
"riverisland.com",
"next.co.uk",
"hush-uk.com",
"monsoon.co.uk",
"janeclayton.co.uk",
"wallsandfloors.co.uk",
"victorianplumbing.co.uk",
"plumbworld.co.uk",
"screwfix.com",
"toolstation.com",
"travisperkins.co.uk",
"wickes.co.uk",
"homedepot.com",
"lowes.com",
"menards.com",
"acehardware.com",
"harborfreight.com",
"northerntool.com",
"sears.com",
"tractorsupply.com",
"grainger.com",
"mcmaster.com",
"fastenal.com",
"uline.com",
"zoro.com",
"quill.com",
"staples.com",
"officedepot.com",
"vistaprint.com",
"cafepress.com",
"zazzle.com",
"shutterfly.com",
"blurb.com",
"snapfish.com",
"mixbook.com",
"photobox.co.uk",
"mpix.com",
"art.com",
"allposters.com",
"desenio.com",
"juniqe.com",
"society6.com",
"redbubble.com",
"teepublic.com",
"threadless.com",
"designbyhumans.com",
"etsy.com",
"notonthehighstreet.com",
"minted.com",
"artfinder.com",
"saatchiart.com",
"ugallery.com",
"20x200.com",
"framedart.com",
"artsy.net",
"1stdibs.com",
"chairish.com",
"dwr.com",
"restorationhardware.com",
"potterybarn.com",
"williams-sonoma.com",
"crateandbarrel.com",
"cb2.com",
"westelm.com",
"overstock.com",
"allmodern.com",
"made.com",
"article.com",
"onekingslane.com",
"serenaandlily.com",
"burrow.com",
"wayfair.co.uk",
"houzz.com",
"jossandmain.com",
"grandinroad.com",
"floydhome.com",
"apt2b.com",
"brooklinen.com",
"parachutehome.com",
"bollbranch.com",
"luxdeco.com",
"jane.com",
"gap.com",
"patagonia.com",
"allsaints.com",
"fjallraven.com",
"ralphlauren.com",
"gant.com",
"harrys.com",
"dollarshaveclub.com",
"warbyparker.com",
"zennioptical.com",
"huckberry.com",
"mrporter.com",
"ssense.com",
"matchesfashion.com",
"theoutnet.com",
"modaoperandi.com",
"lyst.com",
"farfetch.com",
"vestiairecollective.com",
"therealreal.com",
"manicare.com",
"ulta.com",
"sephora.com",
"fentybeauty.com",
"glossier.com",
"beautylish.com",
"cultbeauty.com",
"feelunique.com",
"spacenk.com",
"lookfantastic.com",
"nyxcosmetics.com",
"maccosmetics.com",
"narscosmetics.com",
"urbandecay.com",
"bobbibrowncosmetics.com",
"charlottetilbury.com",
"tomford.com",
"lorealparisusa.com",
"esteelauder.com",
"lancome-usa.com",
"clinique.com",
"shiseido.com",
"dior.com",
"chanel.com",
"gucci.com",
"prada.com",
"louisvuitton.com",
"hermes.com",
"burberry.com",
"balenciaga.com",
"valentino.com",
"versace.com",
"yves-saint-laurent.com",
"jimmychoo.com",
"manoloblahnik.com",
"louboutin.com",
"givenchy.com",
"saintlaurent.com",
"dolcegabbana.com",
"valextra.com",
"miumiu.com",
"celine.com",
"bottegaveneta.com",
"loewe.com",
"todds.com",
"ray-ban.com",
"maui-jim.com",
"oakley.com",
"warbyparker.com",
"glassesusa.com",
"eyebuydirect.com",
"zennioptical.com",
"framesdirect.com",
"saltoptics.com",
"shadyrays.com",
"persol.com",
"hawkersco.com",
"randolphusa.com",
"raen.com",
"diffeyewear.com",
"blenders.com",
"sunglasshut.com",
"misterspex.co.uk",
"krewe.com",
"lenskart.com",
"specsavers.com",
"bonlook.com",
"lenscrafters.com",
"eyekeeper.com",
"contactsdirect.com",
"1800contacts.com",
"coastal.com",
"opticontacts.com",
"discountcontacts.com",
"smartbuyglasses.com",
"goggles4u.com",
"aclens.com",
"lensdirect.com",
"justlenses.com",
"coastalcontacts.com",
"firmoo.com",
"warbyparker.com",
"glasseslit.com",
"percey.com",
"thelensbox.com",
"solluxury.com",
"eyebuydirect.com",
"mouqy.com",
"abbeyeyewear.com",
"optical4less.com",
"ezcontacts.com",
"speckyfoureyes.com",
"glasses.com",
"voguespex.com",
"opticsplanet.com",
"luxreaders.com",
"grandoptical.com",
"smithoptics.com",
"clearly.ca",
"goggles4u.com",
"fashioneyewear.co.uk",
"olympiceyewear.com",
"sporteyes.com",
"shadestation.co.uk",
"blenders.com",
"nathanoptics.com",
"spectacleshoppe.com",
"myeyewear2go.com",
"replacementlenses.net",
"contactlenses.co.uk",
"1800getlens.com",
"justeyewear.com",
"lenspure.com",
"vspdirect.com",
"allaboutvision.com",
"safetyglassesusa.com",
"rx-safety.com",
"elevatesight.com",
"discountcontactlenses.com",
"swimoutlet.com",
"yandy.com",
"victoriassecret.com",
"adoreme.com",
"barenecessities.com",
"honeybirdette.com",
"bravissimo.com",
"fenty.com",
"aerie.com",
"soma.com",
"thirdlove.com",
"agentprovocateur.com",
"fredandginger.com",
"bouxtique.com",
"oysho.com",
"calvinklein.us",
"torrid.com",
"savagex.com",
"knix.com",
"blemishconcepts.com",
"bradelis.com",
"araks.com",
"cougar.com",
"marksandspencer.com",
"nordstromrack.com",
"lakeland.co.uk",
"hollandandbarrett.com",
"boots.com",
"sainsburys.co.uk",
"marksandspencer.com",
"hollandandbarrett.com",
"ocado.com",
"tesco.com",
"waitrose.com",
"asda.com",
"aldi.co.uk",
"lidl.co.uk",
"morrisons.com",
"iceland.co.uk",
"costco.co.uk",
"boots.com",
"superdrug.com",
"bathandbodyworks.com",
"thebodyshop.com",
"lush.com",
"avon.com",
"yvesrocherusa.com",
"kiehls.com",
"lamer.com",
"origins.com",
"clarinsusa.com",
"lancome-usa.com",
"bobbibrowncosmetics.com",
"maybelline.com",
"covergirl.com",
"neutrogena.com",
"cetaphil.com",
"eucerinus.com",
"cera-ve.com",
"nivea.com",
"dove.com",
"olay.com",
"aussiehair.com",
"herbalessences.com",
"tresemme.com",
"johnfrieda.com",
"biore.com",
"biore.com",
"cleanses.com",
"arbonne.com",
"burtsbees.com",
"proactiv.com",
"murad.com",
"paulaschoice.com",
"theordinary.com",
"deciem.com",
"clinique.com",
"shuuemura-usa.com",
"kiehls.com",
"cetaphil.com",
"eucerinus.com",
"cera-ve.com",
"neutrogena.com",
"proactiv.com",
"skinstore.com",
"yesstyle.com",
"cosrx.com",
"missha.com",
"stylevana.com",
"sokoglam.com",
"peachandlily.com",
"banish.com",
"versoskincare.com",
"elemis.com",
"dermstore.com",
"cultbeauty.com",
"feelunique.com",
"spacenk.com",
"lookfantastic.com",
"lovelyskin.com",
"skinceuticals.com",
"dermalogica.com",
"victoriabeckhambeauty.com",
"tatcha.com",
"lushusa.com",
"nyxcosmetics.com",
"urbandecay.com",
"kvdveganbeauty.com",
"anastasiabeverlyhills.com",
"morphe.com",
"colourpop.com",
"jeffreestarcosmetics.com",
"kyliecosmetics.com",
"juviasplace.com",
"beccacosmetics.com",
"toofaced.com",
"smashbox.com",
"benefitcosmetics.com",
"charlottetilbury.com",
"hudabeauty.com",
"fentybeauty.com",
"patmcgrath.com",
"sleekmakeup.com",
"milkmakeup.com",
"gloskinbeauty.com",
"elfcosmetics.com",
"limecrime.com",
"rimmellondon.com",
"maybelline.com",
"lorealparisusa.com",
"revlon.com",
"covergirl.com",
"sallybeauty.com",
"ulta.com",
"sephora.com",
"beautybay.com",
"cultbeauty.com",
"lookfantastic.com",
"feelunique.com",
"spacenk.com",
"boots.com",
"superdrug.com",
"houseoffraser.co.uk",
"johnlewis.com",
"marksandspencer.com",
"debenhams.com",
"next.co.uk",
"clarks.co.uk",
"schuh.co.uk",
"office.co.uk",
"very.co.uk",
"littlewoods.com",
"currys.co.uk",
"argos.co.uk",
"maplin.co.uk",
"richersounds.com",
"pcworld.co.uk",
"scan.co.uk",
"overclockers.co.uk",
"shop.bt.com",
"ebuyer.com",
"dabs.com",
"box.co.uk",
"jessops.com",
"wexphotovideo.com",
"lcegroup.co.uk",
"calumetphoto.co.uk",
"appliancecity.co.uk",
"very.co.uk",
"currys.co.uk",
"screwfix.com",
"wickes.co.uk",
"diy.com",
"homebase.co.uk",
"toolstation.com",
"travisperkins.co.uk",
"victorianplumbing.co.uk",
"plumbworld.co.uk",
"travisperkins.co.uk",
"screwfix.com",
"diy.com",
"homebase.co.uk",
"timberland.co.uk",
"redwing.co.uk",
"wolverine.com",
"kickers.co.uk",
"dr-martens.com",
"catfootwear.co.uk",
"hushpuppies.co.uk",
"toms.co.uk",
"converse.co.uk",
"vans.co.uk",
"skechers.co.uk",
"puma.co.uk",
"asics.co.uk",
"brooksrunning.co.uk",
"newbalance.co.uk",
"saucony.co.uk",
"merrell.co.uk",
"salomon.com",
"theorthoticspeople.co.uk",
"fitflop.co.uk",
"gabor.com",
"ecco.com",
"clarks.co.uk",
"hotter.com",
"schuh.co.uk",
"office.co.uk",
"pavers.co.uk",
"dune.co.uk",
"kurtgeiger.co.uk",
"hobbs.com",
"lkbennett.com",
"radley.co.uk",
"longchamp.com",
"smythson.com",
"montblanc.com",
"moleskine.com",
"moleskine.com",
"smythson.com",
"fossil.com",
"coach.com",
"katespade.com",
"michaelkors.com",
"toryburch.com",
"dooney.com",
"rag-bone.com",
"rebeccaminkoff.com",
"victoriassecret.com",
"calvinklein.us",
"amazon.es",
"amazon.co.uk",
"amazon.de",
"amazon.fr",
"amazon.it",
"alibaba.com",
"alibaba.es",
"alibaba.co.uk",
"alibaba.de",
"alibaba.fr",
"alibaba.it",
"mercadolibre.com",
"mercadolibre.com.ar",
"mercadolibre.com.mx",
"mercadolibre.com.co",
"aliexpress.com",
"aliexpress.es",
"aliexpress.co.uk",
"aliexpress.de",
"aliexpress.fr",
"aliexpress.it",
"guess.com",
"diesel.com",
"levis.com",
"luckybrand.com",
"americanapparel.com",
"gap.com",
"hollisterco.com",
"abercrombie.com",
"express.com",
"jcrew.com",
"banana.com",
"aeo-inc.com",
"uniqlo.com",
"zara.com",
"mango.com",
"bershka.com",
"pullandbear.com",
"stradivarius.com",
"massimodutti.com",
"hm.com",
"primark.com",
"topshop.com",
"missselfridge.com",
"riverisland.com",
"newlook.com",
"urbanoutfitters.com",
"forever21.com",
"charlotterusse.com",
"garageclothing.com",
"pacsun.com",
"boohooltd.com",
"prettylittlething.com",
"shein.com",
"fashionnova.com",
"nastygal.com",
"hellomolly.com",
"revolve.com",
"missguided.com",
"showpo.com",
"lulus.com",
"asos.com",
"zalando.co.uk",
"modcloth.com",
"anthropologie.com",
"freepeople.com",
"ralphlauren.com",
"burberry.com",
"armani.com",
"gucci.com",
"prada.com",
"dior.com",
"fendi.com",
"louisvuitton.com",
"balmain.com",
"versace.com",
"hermes.com",
"ysl.com",
"chanel.com",
"saintlaurent.com",
"loewe.com",
"bottegaveneta.com",
"celine.com",
"miumiu.com",
"valentino.com",
"tods.com",
"jimmychoo.com",
"manoloblahnik.com",
"louboutin.com",
"cartier.com",
"tiffany.com",
"vancleefarpels.com",
"bvlgari.com",
"panerai.com",
"rolex.com",
"tagheuer.com",
"patek.com",
"longines.com",
"audemarspiguet.com",
"omega.com",
"jaeger-lecoultre.com",
"breitling.com",
"hublot.com",
"frankmuller.com",
"ulysse-nardin.com",
"zales.com",
"jared.com",
"kay.com",
"bluenile.com",
"ritani.com",
"jamesallen.com",
"gabrielny.com",
"brilliantearth.com",
"vi.aliexpress.com",
"mercadolibre.com.pe",
"temu.com",
"alibaba.com",
"juntoz.com"
]

# Función para extraer y normalizar el dominio de la URL
def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc or parsed_url.path  # netloc para URLs con protocolo, path para las que no lo tienen
    
    # Remover 'www.' si está presente
    if domain.startswith("www."):
        domain = domain[4:]
        
    # Remover el prefijo 'http://' o 'https://' si está presente
    if domain.startswith("http://"):
        domain = domain[7:]
    elif domain.startswith("https://"):
        domain = domain[8:]

    # Si el dominio aún tiene un '/' al final, removerlo
    domain = domain.rstrip('/')
    
    return domain

# Función para verificar si el dominio existe
def check_domain_exists(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False

# Función para comprobar la similitud del dominio con dominios conocidos
def check_similarity(domain):
    highest_similarity = 0
    best_match = None

    base_domain = domain.split('.')[0]

    for known_domain in KNOWN_DOMAINS:
        known_base_domain = known_domain.split('.')[0]

        if base_domain == known_base_domain:
            if domain == known_domain:
                return 1.0, known_domain  # Exact match
            else:
                return 1.0, known_domain  # Same base domain but different TLD, considered safe

        similarity_ratio = difflib.SequenceMatcher(None, base_domain, known_base_domain).ratio()
        if similarity_ratio > highest_similarity:
            highest_similarity = similarity_ratio
            best_match = known_domain

    return highest_similarity, best_match

@app.route('/api/check_url_similarity', methods=['POST'])
def check_url_similarity():
    data = request.get_json()
    url_to_check = data.get('url')
    
    if not url_to_check:
        return jsonify({"error": "No URL provided"}), 400

    domain = extract_domain(url_to_check)

    try:
        if not check_domain_exists(domain):
            raise Exception("Domain does not exist")

        similarity_ratio, similar_domain = check_similarity(domain)
        
        response = {
            "url": url_to_check,
            "domain": domain,
            "similarity_ratio": similarity_ratio,
            "similar_to": similar_domain if similar_domain else "None"
        }

        if similarity_ratio == 1.0:
            response["status"] = "Safe"
            response["reason"] = "The domain is exactly the same as a known popular site."
            response["ESTADO"] = "legal"
        elif similarity_ratio > 0.7:
            response["status"] = "Insecure"
            response["reason"] = f"The domain is suspiciously similar to {similar_domain}."
            response["ESTADO"] = "fraud"
        else:
            response["status"] = "Safe"
            response["reason"] = "The domain does not closely resemble any known popular sites."
            response["ESTADO"] = "legal"
        
    except Exception as e:
        response = {
            "url": url_to_check,
            "domain": domain,
            "status": "Insecure",
            "reason": str(e),
            "ESTADO": "fraud"
        }
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto asignado por el entorno
    app.run(debug=True, host='0.0.0.0', port=port)  # Asegúrate de escuchar en todas las interfaces
